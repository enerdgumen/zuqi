import asyncio
from unittest.mock import Mock, AsyncMock, call
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

    async def join(self):
        await self.conductor.on_message(self.net, Message(source=self.uid, payload=Box(action='join')))

    async def challenge(self, answer, meanwhile=None):
        async def receive(*_args, **_kwargs):
            if meanwhile:
                await meanwhile()
            if answer:
                return Message(source=self.uid, payload=Box(answer=answer))
            raise asyncio.TimeoutError()

        self.net.receive = receive
        await self.conductor.on_message(self.net, Message(source=self.uid, payload=Box(action='challenge')))

    async def exit(self):
        await self.conductor.on_exit(self.net, self.uid)


async def test_single_player_game():
    net = AsyncMock()
    conductor = Conductor(quiz_source())
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    await mario.enter()
    await mario.join()
    net.publish.assert_called_with(messages.joined('mario'))
    net.send.assert_called_with('mario', messages.question('2+1?'))
    net.reset_mock()
    await mario.challenge(answer=quiz_source.good_answer)
    net.send.assert_called_with('mario', messages.reply(['1', '2', '3', '4']))
    net.publish.assert_has_calls([
        call(messages.challenged('mario')),
        call(messages.won('mario'))
    ])


async def test_notify_other_users_after_join():
    net = AsyncMock()
    conductor = Conductor(quiz_source())
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    luigi = UserEmulator(conductor=conductor, net=net, uid='luigi')
    await mario.enter()
    await luigi.enter()
    await mario.join()
    await luigi.join()
    net.publish.assert_called_with(messages.joined('luigi'))


async def test_notify_other_users_after_challenge():
    net = AsyncMock()
    conductor = Conductor(quiz_source())
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    luigi = UserEmulator(conductor=conductor, net=net, uid='luigi')
    await mario.enter()
    await luigi.enter()
    await mario.join()
    await luigi.join()
    await mario.challenge(answer=quiz_source.good_answer)
    net.publish.assert_any_call(messages.challenged('mario'))


async def test_unjoin_user_after_failed_answer():
    net = AsyncMock()
    conductor = Conductor(quiz_source())
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    await mario.enter()
    await mario.join()
    await mario.challenge(answer=quiz_source.bad_answer)
    net.publish.assert_called_with(messages.lost('mario'))


async def test_unjoin_user_after_answer_timeout():
    net = AsyncMock()
    conductor = Conductor(quiz_source())
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    await mario.enter()
    await mario.join()
    await mario.challenge(answer=None)
    net.publish.assert_called_with(messages.lost('mario'))


async def test_user_cannot_retry_challenge_after_fail():
    net = AsyncMock()
    conductor = Conductor(quiz_source())
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    await mario.enter()
    await mario.join()
    await mario.challenge(answer=quiz_source.bad_answer)
    net.publish.reset_mock()
    await mario.challenge(answer=quiz_source.good_answer)
    net.publish.assert_not_called()


async def test_ignore_other_challenges_during_challenge():
    net = AsyncMock()
    conductor = Conductor(quiz_source())
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    luigi = UserEmulator(conductor=conductor, net=net, uid='luigi')
    await mario.enter()
    await luigi.enter()
    await mario.join()
    await luigi.join()
    net.publish.reset_mock()
    await mario.challenge(answer=quiz_source.good_answer,
                          meanwhile=lambda: luigi.challenge(answer=quiz_source.good_answer))
    net.publish.assert_has_calls([
        call(messages.challenged('mario')),
        call(messages.won('mario'))
    ])


async def test_other_user_can_try_after_failed_challenge():
    net = AsyncMock()
    conductor = Conductor(quiz_source())
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    luigi = UserEmulator(conductor=conductor, net=net, uid='luigi')
    await mario.enter()
    await luigi.enter()
    await mario.join()
    await luigi.join()
    await mario.challenge(answer=quiz_source.bad_answer)
    net.publish.reset_mock()
    await luigi.challenge(answer=quiz_source.good_answer)
    net.publish.assert_has_calls([
        call(messages.challenged('luigi')),
        call(messages.won('luigi'))
    ])


async def test_notify_winner():
    net = AsyncMock()
    conductor = Conductor(quiz_source())
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    await mario.enter()
    await mario.join()
    await mario.challenge(answer=quiz_source.good_answer)
    net.publish.assert_called_with(messages.won('mario'))


async def test_conductor_reply_events_when_new_user_join():
    net = AsyncMock()
    conductor = Conductor(quiz_source())
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    luigi = UserEmulator(conductor=conductor, net=net, uid='luigi')
    peach = UserEmulator(conductor=conductor, net=net, uid='peach')
    await mario.enter()
    await luigi.enter()
    await mario.join()
    await luigi.join()
    await peach.enter()
    await mario.challenge(answer=quiz_source.bad_answer)
    net.send.reset_mock()
    await luigi.challenge(answer=quiz_source.good_answer, meanwhile=lambda: peach.join())
    net.send.assert_has_calls([
        call('peach', messages.joined('luigi')),
        call('peach', messages.challenged('luigi')),
    ])


def quiz_source():
    mock = Mock()
    quiz = Box(question='2+1?', answers=['1', '2', '3', '4'], answer=quiz_source.good_answer)
    mock.next = AsyncMock(return_value=quiz)
    return mock


quiz_source.bad_answer = 1
quiz_source.good_answer = 2
