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
            return await self._handle_join(network, message.user)
        if not self.session.is_user_alive(message.user):
            return
        if messages.is_challenge_request(message) and not self.session.is_challenging():
            return await self._handle_challenge(network, message.user)

    async def _handle_join(self, network, user):
        await network.send(user, messages.question(self.session.quiz.question))
        await self._replay_events(network, user)
        await network.publish(messages.joined(user))
        self.session.add_user(user)

    async def _replay_events(self, network, user):
        for other_user, alive in self.session.users.items():
            if alive:
                await network.send(user, messages.joined(other_user))
        if self.session.challenging:
            await network.send(user, messages.challenged(self.session.challenging))

    async def _handle_challenge(self, network, user):
        try:
            self.session.begin_challenge(user)
            await network.send(user, messages.reply(self.session.quiz.answers))
            await network.publish(messages.challenged(user))
            try:
                answer = await network.receive(user, timeout=challenge_timeout_seconds)
                await self._handle_answer(network, answer)
            except asyncio.TimeoutError:
                await self._handle_bad_answer(network, user)
        finally:
            self.session.end_challenge()

    async def _handle_answer(self, network, message):
        ok = message.body.answer == self.session.quiz.answer
        if ok:
            await self._handle_good_answer(network, message.user)
        else:
            await self._handle_bad_answer(network, message.user)

    async def _handle_good_answer(self, network, user):
        await self._end_game(network, winner=user)

    async def _handle_bad_answer(self, network, user):
        self.session.kill_user(user)
        await network.publish(messages.lost(user))
        if not self.session.is_any_user_alive():
            await self._end_game(network, winner=None)

    async def _end_game(self, network, winner):
        await network.publish(messages.end(winner))
        await self.new_session()

    async def on_exit(self, network, user):
        await self._handle_bad_answer(network, user)
