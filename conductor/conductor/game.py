import asyncio

from conductor import messages


class Session:
    def __init__(self, quiz):
        self.quiz = quiz
        self.users = set()
        self.dead_users = set()
        self.challenging = None

    def add_user(self, user):
        self.users.add(user)

    def remove_user(self, user):
        self.users.remove(user)

    def kill_user(self, user):
        self.dead_users.add(user)

    def is_user_present(self, user):
        return user in self.users

    def is_user_alive(self, user):
        return user not in self.dead_users

    def is_any_user_alive(self):
        return len(self.users) > len(self.dead_users)

    def is_challenging(self):
        return self.challenging

    def begin_challenge(self, user):
        self.challenging = user

    def end_challenge(self):
        self.challenging = None

    def new_quiz(self, quiz):
        self.quiz = quiz
        self.challenging = None
        self.dead_users = set()


class Conductor:
    def __init__(self,
                 quiz_source,
                 challenge_timeout_seconds,
                 seconds_before_new_session,
                 ):
        self.quiz_source = quiz_source
        self.challenge_timeout_seconds = challenge_timeout_seconds
        self.seconds_before_new_session = seconds_before_new_session
        self.session = None

    async def new_session(self):
        quiz = await self.quiz_source.next()
        if self.session:
            self.session.new_quiz(quiz)
        else:
            self.session = Session(quiz)

    async def on_enter(self, network, user):
        if not self.session:
            await self.new_session()
        await network.send(user, messages.question(self.session.quiz.question))
        await self._replay_events(network, user)
        await network.publish(messages.joined(user))
        self.session.add_user(user)

    async def on_message(self, network, message):
        if not self.session.is_user_alive(message.user):
            return
        if messages.is_challenge_request(message) and not self.session.is_challenging():
            return await self._handle_challenge(network, message.user)

    async def _replay_events(self, network, user):
        for other_user in self.session.users:
            await network.send(user, messages.joined(other_user))
            if not self.session.is_user_alive(other_user):
                await network.send(user, messages.lost(other_user))
        if not self.session.is_user_alive(user):
            await network.send(user, messages.lost(user))
        if self.session.challenging:
            await network.send(user, messages.challenged(self.session.challenging))

    async def _handle_challenge(self, network, user):
        try:
            self.session.begin_challenge(user)
            await network.send(user, messages.reply(self.session.quiz.answers, self.challenge_timeout_seconds))
            await network.publish(messages.challenged(user))
            try:
                answer = await network.receive(user, timeout=self.challenge_timeout_seconds)
                await self._handle_answer(network, answer)
            except asyncio.TimeoutError:
                await self._handle_bad_answer(network, user, 'timeout')
        finally:
            self.session.end_challenge()

    async def _handle_answer(self, network, message):
        ok = message.body.answer == self.session.quiz.answer
        if ok:
            await self._handle_good_answer(network, message.user)
        else:
            await self._handle_bad_answer(network, message.user, 'incorrect')

    async def _handle_good_answer(self, network, user):
        await self._end_game(network, winner=user)

    async def _handle_bad_answer(self, network, user, reason):
        self.session.kill_user(user)
        await network.publish(messages.lost(user, reason))
        if not self.session.is_any_user_alive():
            await self._end_game(network, winner=None)

    async def _end_game(self, network, winner):
        await network.publish(messages.end(winner, answer=self.session.quiz.answer))
        await asyncio.sleep(self.seconds_before_new_session)
        await self.new_session()
        await network.publish(messages.question(self.session.quiz.question))

    async def on_exit(self, network, user):
        self.session.remove_user(user)
        if self.session.challenging == user:
            self.session.kill_user(user)
            self.session.end_challenge()
            await network.publish(messages.lost(user, reason='exit'))
        await network.publish(messages.left(user))
