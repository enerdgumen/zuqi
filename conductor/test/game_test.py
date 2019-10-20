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

    async def challenge_and_answer(self, answer):
        self.net.receive = AsyncMock(return_value=Message(source=self.uid, payload=Box(answer=answer)))
        await self.conductor.on_message(self.net, Message(source=self.uid, payload=Box(action='challenge')))

    async def challenge_without_answer(self):
        def raise_timeout(*args, **kwargs):
            raise asyncio.TimeoutError()

        self.net.receive = raise_timeout
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
    await mario.challenge_and_answer(2)
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
    await mario.challenge_and_answer(2)
    net.publish.assert_any_call(Box(event='challenging', user='mario'))


async def test_unjoin_user_after_failed_answer():
    net = AsyncMock()
    conductor = Conductor(quiz_source())
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    await mario.enter()
    await mario.join()
    await mario.challenge_and_answer(1)
    net.publish.assert_called_with(Box(event='removed', user='mario'))


async def test_unjoin_user_after_answer_timeout():
    net = AsyncMock()
    conductor = Conductor(quiz_source())
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    await mario.enter()
    await mario.join()
    await mario.challenge_without_answer()
    net.publish.assert_called_with(Box(event='removed', user='mario'))


async def test_notify_winner():
    net = AsyncMock()
    conductor = Conductor(quiz_source())
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    await mario.enter()
    await mario.join()
    await mario.challenge_and_answer(2)
    net.publish.assert_called_with(Box(event='winner', user='mario'))


def quiz_source():
    mock = Mock()
    mock.next = AsyncMock(return_value=Box(question='2+1?', answers=['1', '2', '3', '4'], answer=2))
    return mock
