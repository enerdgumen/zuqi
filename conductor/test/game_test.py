import asyncio
from unittest.mock import Mock, AsyncMock, call
from box import Box
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
    net.publish.assert_called_with(Box(event='joined', user='mario'))
    net.send.assert_called_with('mario', Box(question='2+1?'))
    net.reset_mock()
    await mario.challenge(answer=2)
    net.send.assert_called_with('mario', Box(action='reply', answers=['1', '2', '3', '4']))
    net.publish.assert_has_calls([
        call(Box(event='challenging', user='mario')),
        call(Box(event='winner', user='mario'))
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
    net.publish.assert_called_with(Box(event='joined', user='luigi'))


async def test_notify_other_users_after_challenge():
    net = AsyncMock()
    conductor = Conductor(quiz_source())
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    luigi = UserEmulator(conductor=conductor, net=net, uid='luigi')
    await mario.enter()
    await luigi.enter()
    await mario.join()
    await luigi.join()
    await mario.challenge(answer=2)
    net.publish.assert_any_call(Box(event='challenging', user='mario'))


async def test_unjoin_user_after_failed_answer():
    net = AsyncMock()
    conductor = Conductor(quiz_source())
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    await mario.enter()
    await mario.join()
    await mario.challenge(answer=1)
    net.publish.assert_called_with(Box(event='loser', user='mario'))


async def test_unjoin_user_after_answer_timeout():
    net = AsyncMock()
    conductor = Conductor(quiz_source())
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    await mario.enter()
    await mario.join()
    await mario.challenge(answer=None)
    net.publish.assert_called_with(Box(event='loser', user='mario'))


async def test_user_cannot_retry_challenge_after_fail():
    net = AsyncMock()
    conductor = Conductor(quiz_source())
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    await mario.enter()
    await mario.join()
    await mario.challenge(answer=1)
    net.publish.reset_mock()
    await mario.challenge(answer=2)
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
    await mario.challenge(answer=2, meanwhile=lambda: luigi.challenge(answer=2))
    net.publish.assert_has_calls([
        call(Box(event='challenging', user='mario')),
        call(Box(event='winner', user='mario'))
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
    await mario.challenge(answer=1)
    net.publish.reset_mock()
    await luigi.challenge(answer=2)
    net.publish.assert_has_calls([
        call(Box(event='challenging', user='luigi')),
        call(Box(event='winner', user='luigi'))
    ])


async def test_notify_winner():
    net = AsyncMock()
    conductor = Conductor(quiz_source())
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    await mario.enter()
    await mario.join()
    await mario.challenge(answer=2)
    net.publish.assert_called_with(Box(event='winner', user='mario'))


def quiz_source():
    mock = Mock()
    mock.next = AsyncMock(return_value=Box(question='2+1?', answers=['1', '2', '3', '4'], answer=2))
    return mock
