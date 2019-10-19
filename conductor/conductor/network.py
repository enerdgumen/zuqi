from collections import namedtuple
import logging
from uuid import uuid4

from aiohttp import WSMsgType, web
from box import Box

Message = namedtuple('Message', ['source', 'payload'])


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
        sid = self.registry.register(ws)
        await self.on_enter(self, sid)
        while True:
            msg = await ws.receive()
            logging.debug('%s: received %s', sid, msg)
            if msg.type == WSMsgType.text:
                await self._handle_message(sid, msg)
            elif msg.type == WSMsgType.ERROR:
                logging.exception('socket error', ws.exception())
            elif msg.type == WSMsgType.CLOSE:
                break
            else:
                logging.warning('unexpected message %s', msg.type)
        self.registry.unregister(sid)
        await self.on_exit(self, sid)
        return ws

    async def _handle_message(self, sid, msg):
        try:
            message = Message(source=sid, payload=Box(msg.json()))
            await self.on_message(self, message)
        except:
            logging.exception('cannot handle message %s', msg)

    async def send(self, sid, payload):
        logging.debug('%s: sending %s', sid, payload)
        ws = self.registry.sockets[sid]
        await ws.send_json(payload)

    async def publish(self, payload):
        logging.debug('publishing %s', payload)
        for ws in self.registry.sockets.values():
            await ws.send_json(payload)

    async def receive(self, sid, timeout=None):
        logging.debug('%s: waiting for message', sid)
        ws = self.registry.sockets[sid]
        payload = await ws.receive_json(timeout=timeout)
        logging.debug('%s: received %s', sid, payload)
        return Message(source=sid, payload=Box(payload))

    async def close(self):
        for sid, ws in self.registry.sockets.items():
            await ws.close()
            self.registry.unregister(sid)


class SocketRegistry:
    def __init__(self):
        self.sockets = {}

    def register(self, ws):
        sid = str(uuid4())
        self.sockets[sid] = ws
        logging.debug('%s: registered socket', sid)
        return sid

    def unregister(self, sid):
        del self.sockets[sid]
        logging.debug('%s: unregistered socket', sid)
