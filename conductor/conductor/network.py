from collections import namedtuple
import logging
from uuid import uuid4

from aiohttp import WSMsgType, web
from box import Box

Message = namedtuple('Message', ['user', 'body'])


async def noop(*_args):
    pass


class Network:
    def __init__(self, on_enter=noop, on_message=noop, on_exit=noop):
        self.registry = SocketRegistry()
        self.on_enter = on_enter
        self.on_message = on_message
        self.on_exit = on_exit

    async def __call__(self, request):
        ws = web.WebSocketResponse()
        ws_ready = ws.can_prepare(request)
        if not ws_ready.ok:
            raise web.HTTPMethodNotAllowed()
        await ws.prepare(request)
        user = self.registry.register(ws)
        await self.on_enter(self, user)
        while True:
            msg = await ws.receive()
            logging.debug('%s: received %s', user, msg)
            if msg.type == WSMsgType.text:
                await self._handle_message(user, msg)
            elif msg.type == WSMsgType.ERROR:
                logging.exception('socket error', ws.exception())
            elif msg.type == WSMsgType.CLOSE:
                break
            else:
                logging.warning('unexpected message %s', msg.type)
        self.registry.unregister(user)
        await self.on_exit(self, user)
        return ws

    async def _handle_message(self, user, msg):
        try:
            message = Message(user=user, body=Box(msg.json()))
            await self.on_message(self, message)
        except:
            logging.exception('cannot handle message %s', msg)

    async def send(self, user, body):
        logging.debug('%s: sending %s', user, body)
        ws = self.registry.sockets[user]
        await ws.send_json(body)

    async def publish(self, body):
        logging.debug('publishing %s', body)
        for ws in self.registry.sockets.values():
            await ws.send_json(body)

    async def receive(self, user, timeout=None):
        logging.debug('%s: waiting for message', user)
        ws = self.registry.sockets[user]
        body = await ws.receive_json(timeout=timeout)
        logging.debug('%s: received %s', user, body)
        return Message(user=user, body=Box(body))

    async def close(self):
        for user, ws in self.registry.sockets.items():
            await ws.close()
            self.registry.unregister(user)


class SocketRegistry:
    def __init__(self):
        self.sockets = {}

    def register(self, ws):
        user = str(uuid4())
        self.sockets[user] = ws
        logging.debug('%s: registered socket', user)
        return user

    def unregister(self, user):
        del self.sockets[user]
        logging.debug('%s: unregistered socket', user)
