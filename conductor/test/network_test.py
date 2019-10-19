from unittest.mock import Mock

from conductor.network import Network
from conductor.server import application


async def test_enter_event(aiohttp_client):
    mock = Mock()
    network = Network(on_enter=mock)
    client = await aiohttp_client(application(network))
    await client.ws_connect('/')
    sid = mock.call_args[1]
    assert sid is not None


async def test_send(aiohttp_client):
    async def echo(net, message):
        await net.send(message.source, message.payload)

    network = Network(on_message=echo)
    client = await aiohttp_client(application(network))
    ws = await client.ws_connect('/')
    await ws.send_json(123)
    got = await ws.receive_json(timeout=1)
    assert got == 123


async def test_publish(aiohttp_client):
    async def broadcast_echo(net, message):
        await net.publish(message.payload)

    network = Network(on_message=broadcast_echo)
    client = await aiohttp_client(application(network))
    ws1 = await client.ws_connect('/')
    ws2 = await client.ws_connect('/')
    await ws1.send_json(123)
    got = await ws1.receive_json(timeout=1)
    assert got == 123
    got = await ws2.receive_json(timeout=1)
    assert got == 123


async def test_exit_event(aiohttp_client):
    mock = Mock()
    network = Network(on_exit=mock)
    client = await aiohttp_client(application(network))
    ws = await client.ws_connect('/')
    await ws.close()
    sid = mock.call_args[1]
    assert sid is not None
