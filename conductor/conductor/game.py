import asyncio

from conductor import messages
from conductor.config import challenge_timeout_seconds


class Session:
    def __init__(self, quiz):
        self.quiz = quiz
        self.users = {}
        self.challenging = None

    def add_user(self, user):
        self.users[user] = True

    def kill_user(self, user):
        self.users[user] = False

    def is_user_present(self, user):
        return user in self.users

    def is_user_alive(self, user):
        return self.users.get(user, False)

    def is_any_user_alive(self):
        return any(self.users.values())

    def is_challenging(self):
        return self.challenging

    def begin_challenge(self, user):
        self.challenging = user

    def end_challenge(self):
        self.challenging = None


class Conductor:
    def __init__(self, quiz_source):
        self.quiz_source = quiz_source
        self.session = None

    async def new_session(self):
        quiz = await self.quiz_source.next()
        self.session = Session(quiz)

    async def on_enter(self, _network, _user):
        if not self.session:
            await self.new_session()

    async def on_message(self, network, message):
        if messages.is_join_request(message) and not self.session.is_user_present(message.user):
            return await self._handle_join(network, message)
        if not self.session.is_user_alive(message.user):
            return
        if messages.is_challenge_request(message) and not self.session.is_challenging():
            return await self._handle_challenge(network, message)

    async def _handle_join(self, network, message):
        await network.send(message.user, messages.question(self.session.quiz.question))
        await self._replay_events(network, message)
        await network.publish(messages.joined(message.user))
        self.session.add_user(message.user)

    async def _replay_events(self, network, message):
        for user, active in self.session.users.items():
            if active:
                await network.send(message.user, messages.joined(user))
        if self.session.challenging:
            await network.send(message.user, messages.challenged(self.session.challenging))

    async def _handle_challenge(self, network, message):
        try:
            self.session.begin_challenge(message.user)
            await network.send(message.user, messages.reply(self.session.quiz.answers))
            await network.publish(messages.challenged(message.user))
            try:
                message = await network.receive(message.user, timeout=challenge_timeout_seconds)
                await self._handle_answer(network, message)
            except asyncio.TimeoutError:
                await self._handle_bad_answer(network, message)
        finally:
            self.session.end_challenge()

    async def _handle_answer(self, network, message):
        ok = message.body.answer == self.session.quiz.answer
        if ok:
            await self._handle_good_answer(network, message)
        else:
            await self._handle_bad_answer(network, message)

    async def _handle_good_answer(self, network, message):
        await self._end_game(network, winner=message.user)

    async def _handle_bad_answer(self, network, message):
        self.session.kill_user(message.user)
        await network.publish(messages.lost(message.user))
        if not self.session.is_any_user_alive():
            await self._end_game(network, winner=None)

    async def _end_game(self, network, winner):
        await network.publish(messages.end(winner))
        await self.new_session()

    async def on_exit(self, network, user):
        pass
