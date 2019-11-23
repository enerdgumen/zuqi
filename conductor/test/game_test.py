import asyncio
from itertools import cycle
from unittest.mock import AsyncMock, call
from box import Box

from conductor import messages
from conductor.game import Conductor
from conductor.network import Message


class UserEmulator:
    def __init__(self, conductor, net, uid):
        self.conductor = conductor
        self.net = net
        self.uid = uid
        self.answer = None

    async def enter(self):
        await self.conductor.on_enter(self.net, self.uid)

    async def challenge(self, answer, meanwhile=None):
        async def receive(*_args, **_kwargs):
            if meanwhile:
                await meanwhile()
            if answer:
                return Message(user=self.uid, body=Box(answer=answer))
            raise asyncio.TimeoutError()

        self.net.receive = receive
        await self.conductor.on_message(self.net, Message(user=self.uid, body=Box(action='challenge')))

    async def exit(self):
        await self.conductor.on_exit(self.net, self.uid)


async def test_single_player_game():
    net = AsyncMock()
    conductor = Conductor(
        quiz_source=MockQuizSource(),
        challenge_timeout_seconds=3,
        seconds_before_new_session=0,
    )
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    await mario.enter()
    net.publish.assert_called_with(messages.joined('mario'))
    net.send.assert_called_with('mario', messages.question('1+2?'))
    net.reset_mock()
    await mario.challenge(answer=MockQuizSource.good_answer)
    net.send.assert_called_with('mario', messages.reply(['1', '2', '3', '4'], timeout=3))
    net.publish.assert_has_calls([
        call(messages.challenged('mario')),
        call(messages.end('mario', answer=2))
    ])


async def test_notify_other_users_after_join():
    net = AsyncMock()
    conductor = Conductor(
        quiz_source=MockQuizSource(),
        challenge_timeout_seconds=5,
        seconds_before_new_session=0,
    )
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    luigi = UserEmulator(conductor=conductor, net=net, uid='luigi')
    await mario.enter()
    await luigi.enter()
    net.publish.assert_called_with(messages.joined('luigi'))


async def test_notify_other_users_after_challenge():
    net = AsyncMock()
    conductor = Conductor(
        quiz_source=MockQuizSource(),
        challenge_timeout_seconds=5,
        seconds_before_new_session=0,
    )
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    luigi = UserEmulator(conductor=conductor, net=net, uid='luigi')
    await mario.enter()
    await luigi.enter()
    await mario.challenge(answer=MockQuizSource.good_answer)
    net.publish.assert_any_call(messages.challenged('mario'))


async def test_unjoin_user_after_failed_answer():
    net = AsyncMock()
    conductor = Conductor(
        quiz_source=MockQuizSource(),
        challenge_timeout_seconds=5,
        seconds_before_new_session=0,
    )
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    await mario.enter()
    await mario.challenge(answer=MockQuizSource.bad_answer)
    net.publish.assert_any_call(messages.lost('mario', reason='incorrect'))


async def test_unjoin_user_after_answer_timeout():
    net = AsyncMock()
    conductor = Conductor(
        quiz_source=MockQuizSource(),
        challenge_timeout_seconds=5,
        seconds_before_new_session=0,
    )
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    await mario.enter()
    await mario.challenge(answer=None)
    net.publish.assert_any_call(messages.lost('mario', reason='timeout'))


async def test_user_in_challenge_lose_on_exit():
    def fail_receive():
        raise RuntimeError()
    net = AsyncMock()
    conductor = Conductor(
        quiz_source=MockQuizSource(),
        challenge_timeout_seconds=5,
        seconds_before_new_session=0,
    )
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    luigi = UserEmulator(conductor=conductor, net=net, uid='luigi')
    await mario.enter()
    await luigi.enter()
    await mario.challenge(answer=None, meanwhile=fail_receive)
    await mario.exit()
    net.publish.assert_any_call(messages.lost('mario', reason=None))


async def test_user_cannot_retry_challenge_after_fail():
    net = AsyncMock()
    conductor = Conductor(
        quiz_source=MockQuizSource(),
        challenge_timeout_seconds=5,
        seconds_before_new_session=0,
    )
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    luigi = UserEmulator(conductor=conductor, net=net, uid='luigi')
    await mario.enter()
    await luigi.enter()
    await mario.challenge(answer=MockQuizSource.bad_answer)
    net.publish.reset_mock()
    await mario.challenge(answer=MockQuizSource.good_answer)
    net.publish.assert_not_called()


async def test_ignore_other_challenges_during_challenge():
    net = AsyncMock()
    conductor = Conductor(
        quiz_source=MockQuizSource(),
        challenge_timeout_seconds=5,
        seconds_before_new_session=0,
    )
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    luigi = UserEmulator(conductor=conductor, net=net, uid='luigi')
    await mario.enter()
    await luigi.enter()
    net.publish.reset_mock()
    await mario.challenge(answer=MockQuizSource.good_answer,
                          meanwhile=lambda: luigi.challenge(answer=MockQuizSource.good_answer))
    net.publish.assert_has_calls([
        call(messages.challenged('mario')),
        call(messages.end('mario', answer=MockQuizSource.good_answer))
    ])


async def test_other_user_can_try_after_failed_challenge():
    net = AsyncMock()
    conductor = Conductor(
        quiz_source=MockQuizSource(),
        challenge_timeout_seconds=5,
        seconds_before_new_session=0,
    )
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    luigi = UserEmulator(conductor=conductor, net=net, uid='luigi')
    await mario.enter()
    await luigi.enter()
    await mario.challenge(answer=MockQuizSource.bad_answer)
    net.publish.reset_mock()
    await luigi.challenge(answer=MockQuizSource.good_answer)
    net.publish.assert_has_calls([
        call(messages.challenged('luigi')),
        call(messages.end('luigi', answer=MockQuizSource.good_answer))
    ])


async def test_notify_winner():
    net = AsyncMock()
    conductor = Conductor(
        quiz_source=MockQuizSource(),
        challenge_timeout_seconds=5,
        seconds_before_new_session=0,
    )
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    await mario.enter()
    await mario.challenge(answer=MockQuizSource.good_answer)
    net.publish.assert_has_calls([
        call(messages.end('mario', answer=MockQuizSource.good_answer))
    ])


async def test_conductor_reply_events_when_new_user_join():
    net = AsyncMock()
    conductor = Conductor(
        quiz_source=MockQuizSource(),
        challenge_timeout_seconds=5,
        seconds_before_new_session=0,
    )
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    luigi = UserEmulator(conductor=conductor, net=net, uid='luigi')
    peach = UserEmulator(conductor=conductor, net=net, uid='peach')
    await mario.enter()
    await luigi.enter()
    await mario.challenge(answer=MockQuizSource.bad_answer)
    net.send.reset_mock()
    await luigi.challenge(answer=MockQuizSource.good_answer, meanwhile=lambda: peach.enter())
    net.send.assert_has_calls([
        call('peach', messages.joined('mario')),
        call('peach', messages.lost('mario')),
        call('peach', messages.joined('luigi')),
        call('peach', messages.challenged('luigi'))
    ], any_order=True)


async def test_end_game_when_all_users_lose():
    net = AsyncMock()
    conductor = Conductor(
        quiz_source=MockQuizSource(),
        challenge_timeout_seconds=5,
        seconds_before_new_session=0,
    )
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    luigi = UserEmulator(conductor=conductor, net=net, uid='luigi')
    await mario.enter()
    await luigi.enter()
    await mario.challenge(answer=MockQuizSource.bad_answer)
    await luigi.challenge(answer=MockQuizSource.bad_answer)
    net.publish.assert_any_call(messages.end(winner=None, answer=MockQuizSource.good_answer))


async def test_new_session_is_created_after_end():
    net = AsyncMock()
    conductor = Conductor(
        quiz_source=MockQuizSource(),
        challenge_timeout_seconds=5,
        seconds_before_new_session=0,
    )
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    await mario.enter()
    net.send.assert_any_call('mario', messages.question('1+2?'))
    await mario.challenge(answer=MockQuizSource.bad_answer)
    net.publish.assert_any_call(messages.question('2+1?'))


class MockQuizSource:
    bad_answer = 1
    good_answer = 2

    def __init__(self):
        self.quiz = cycle([
            Box(question='1+2?', answers=['1', '2', '3', '4'], answer=self.good_answer),
            Box(question='2+1?', answers=['1', '2', '3', '4'], answer=self.good_answer)
        ])

    async def next(self):
        return next(self.quiz)
