from unittest.mock import AsyncMock

from box import Box

from conductor.network import Network
from conductor.server import application


async def test_connect_require_uid(aiohttp_client):
    network = Network()
    client = await aiohttp_client(application(network, shutdown=AsyncMock()))
    with pytest.raises(aiohttp.WSServerHandshakeError):
        await client.ws_connect('/?uid=')


async def test_enter_event(aiohttp_client):
    mock = AsyncMock()
    network = Network(on_enter=mock)
    client = await aiohttp_client(application(network, shutdown=mock))
    await client.ws_connect('/?uid=name')
    sid = mock.call_args[1]
    assert sid is not None


async def test_send(aiohttp_client):
    async def echo(net, message):
        await net.send(message.user, message.body)

    network = Network(on_message=echo)
    client = await aiohttp_client(application(network, shutdown=AsyncMock()))
    ws = await client.ws_connect('/?uid=name')
    await ws.send_json(Box(x=1))
    got = await ws.receive_json(timeout=3)
    assert got == Box(x=1)


async def test_publish(aiohttp_client):
    async def broadcast_echo(net, message):
        await net.publish(message.body)

    network = Network(on_message=broadcast_echo)
    client = await aiohttp_client(application(network, shutdown=AsyncMock()))
    ws1 = await client.ws_connect('/?uid=name1')
    ws2 = await client.ws_connect('/?uid=name2')
    await ws1.send_json(Box(x=1))
    got = await ws1.receive_json(timeout=1)
    assert got == Box(x=1)
    got = await ws2.receive_json(timeout=1)
    assert got == Box(x=1)


async def test_exit_event(aiohttp_client):
    mock = AsyncMock()
    network = Network(on_exit=mock)
    client = await aiohttp_client(application(network, shutdown=mock))
    ws = await client.ws_connect('/?uid=name')
    await ws.close()
    sid = mock.call_args[1]
    assert sid is not None
