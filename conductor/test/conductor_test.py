from unittest.mock import Mock, AsyncMock
from box import Box
from conductor.conductor import Conductor
from conductor.network import Message


class UserEmulator:
    def __init__(self, conductor, net, uid):
        self.conductor = conductor
        self.net = net
        self.uid = uid

    async def enter(self):
        await self.conductor.on_enter(self.net, self.uid)

    async def join(self):
        await self.conductor.on_message(self.net, Message(source=self.uid, payload=Box(action='join')))

    async def challenge(self):
        await self.conductor.on_message(self.net, Message(source=self.uid, payload=Box(action='challenge')))

    async def answer(self, index):
        await self.conductor.on_message(self.net, Message(source=self.uid, payload=Box(action='answer', answer=index)))

    async def exit(self):
        await self.conductor.on_exit(self.net, self.uid)


async def test_single_player_game():
    net = AsyncMock()
    conductor = Conductor(quiz_source())
    await conductor.new_session()
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    await mario.enter()
    await mario.join()
    net.publish.assert_called_with(Box(event='joined', user='mario'))
    net.send.assert_called_with('mario', Box(question='2+1?'))
    await mario.challenge()
    net.publish.assert_called_with(Box(event='challenging', user='mario'))
    net.send.assert_called_with('mario', Box(action='reply', answers=['1', '2', '3', '4']))
    await mario.answer(2)
    net.publish.assert_called_with(Box(event='winner', user='mario'))
    await mario.exit()


async def test_unjoin_user_after_failed_answer():
    net = AsyncMock()
    conductor = Conductor(quiz_source())
    await conductor.new_session()
    mario = UserEmulator(conductor=conductor, net=net, uid='mario')
    await mario.enter()
    await mario.join()
    await mario.challenge()
    await mario.answer(1)
    net.publish.assert_called_with(Box(event='removed', user='mario'))
    net.reset_mock()
    await mario.answer(2)
    net.publish.assert_not_called()


def quiz_source():
    mock = Mock()
    mock.next = AsyncMock(return_value=Box(question='2+1?', answers=['1', '2', '3', '4'], answer=2))
    return mock
