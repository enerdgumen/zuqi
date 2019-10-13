import pytest

from conductor.server import application


@pytest.mark.timeout(1)
async def test_send(aiohttp_client):
    async def echo(network, message):
        await network.send(message.source, message.payload)

    client = await aiohttp_client(application(echo))
    ws = await client.ws_connect('/')
    await ws.send_json(123)
    got = await ws.receive_json()
    assert got == 123


@pytest.mark.timeout(1)
async def test_publish(aiohttp_client):
    async def broadcast_echo(network, message):
        await network.publish(message.source, message.payload)

    client = await aiohttp_client(application(broadcast_echo))
    ws1 = await client.ws_connect('/')
    ws2 = await client.ws_connect('/')
    await ws1.send_json(123)
    got = await ws1.receive_json()
    assert got == 123
    got = await ws2.receive_json()
    assert got == 123
