from unittest.mock import AsyncMock

import aiohttp
from box import Box
import pytest

from conductor.network import Network
from conductor.registry import SocketRegistry
from conductor.server import application


async def test_connect_require_uid(aiohttp_client):
    registry = SocketRegistry(max_sockets=1)
    network = Network(registry)
    client = await aiohttp_client(application(network, shutdown=AsyncMock()))
    with pytest.raises(aiohttp.WSServerHandshakeError):
        await client.ws_connect('/play?uid=')


async def test_cannot_connect_clients_with_same_uid(aiohttp_client):
    registry = SocketRegistry(max_sockets=2)
    network = Network(registry)
    client = await aiohttp_client(application(network, shutdown=AsyncMock()))
    await client.ws_connect('/play?uid=id')
    ws = await client.ws_connect('/play?uid=id')
    got = await ws.receive_json()
    assert got == Box(event='rejected', reason='usernameNotAvailable')


async def test_cannot_exceed_max_sockets_limit(aiohttp_client):
    registry = SocketRegistry(max_sockets=1)
    network = Network(registry)
    client = await aiohttp_client(application(network, shutdown=AsyncMock()))
    await client.ws_connect('/play?uid=id')
    ws = await client.ws_connect('/play?uid=id')
    got = await ws.receive_json()
    assert got == Box(event='rejected', reason='maxSocketsReached')


async def test_send_ready_event_after_connection(aiohttp_client):
    registry = SocketRegistry(max_sockets=1)
    network = Network(registry)
    client = await aiohttp_client(application(network, shutdown=AsyncMock()))
    ws = await client.ws_connect('/play?uid=id')
    got = await ws.receive_json()
    assert got == Box(event='ready')


async def test_enter_event(aiohttp_client):
    registry = SocketRegistry(max_sockets=1)
    on_enter = AsyncMock()
    network = Network(registry, on_enter=on_enter)
    client = await aiohttp_client(application(network, shutdown=AsyncMock()))
    await client.ws_connect('/play?uid=name')
    on_enter.assert_called_with(network, 'name')


async def test_send(aiohttp_client):
    async def echo(net, message):
        await net.send(message.user, message.body)

    registry = SocketRegistry(max_sockets=1)
    network = Network(registry, on_message=echo)
    client = await aiohttp_client(application(network, shutdown=AsyncMock()))
    ws = await client.ws_connect('/play?uid=name')
    await ws.receive_json()  # receive ready event
    await ws.send_json(Box(x=1))
    got = await ws.receive_json(timeout=3)
    assert got == Box(x=1)


async def test_publish(aiohttp_client):
    async def broadcast_echo(net, message):
        await net.publish(message.body)

    registry = SocketRegistry(max_sockets=2)
    network = Network(registry, on_message=broadcast_echo)
    client = await aiohttp_client(application(network, shutdown=AsyncMock()))
    ws1 = await client.ws_connect('/play?uid=name1')
    ws2 = await client.ws_connect('/play?uid=name2')
    await ws1.receive_json()  # receive ready event
    await ws2.receive_json()  # receive ready event
    await ws1.send_json(Box(x=1))
    got = await ws1.receive_json(timeout=1)
    assert got == Box(x=1)
    got = await ws2.receive_json(timeout=1)
    assert got == Box(x=1)


async def test_exit_event(aiohttp_client):
    registry = SocketRegistry(max_sockets=1)
    on_exit = AsyncMock()
    network = Network(registry, on_exit=on_exit)
    client = await aiohttp_client(application(network, shutdown=on_exit))
    ws = await client.ws_connect('/play?uid=name')
    await ws.close()
    on_exit.assert_called_with(network, 'name')
