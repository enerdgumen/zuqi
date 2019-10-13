import logging
from collections import namedtuple
from uuid import uuid4
from aiohttp import web, WSMsgType

Message = namedtuple('Message', ['source', 'payload'])


class Network:
    def __init__(self, handler):
        self.registry = SocketRegistry()
        self.handler = handler

    async def __call__(self, request):
        ws = web.WebSocketResponse()
        ws_ready = ws.can_prepare(request)
        if not ws_ready.ok:
            raise web.HTTPMethodNotAllowed()
        await ws.prepare(request)
        sid = self.registry.register(ws)
        while True:
            msg = await ws.receive()
            if msg.type == WSMsgType.text:
                await self._handle_message(sid, msg)
            elif msg.type == WSMsgType.ERROR:
                logging.exception('socket error', ws.exception())
            elif msg.type == WSMsgType.CLOSE:
                break
            else:
                logging.warning('unexpected message %s', msg.type)
        self.registry.unregister(sid)
        return ws

    async def _handle_message(self, sid, msg):
        try:
            message = Message(
                source=sid,
                payload=msg.json()
            )
            await self.handler(self, message)
        except:
            logging.exception('cannot handle message %s', msg)

    async def send(self, sid, payload):
        ws = self.registry.sockets[sid]
        await ws.send_json(payload)

    async def publish(self, payload):
        for ws in self.registry.sockets.values():
            await ws.send_json(payload)

    async def close(self):
        for sid, ws in self.registry.sockets.items():
            await ws.close()
            self.registry.unregister(sid)


class SocketRegistry:
    def __init__(self):
        self.sockets = {}

    def register(self, ws):
        sid = uuid4()
        self.sockets[sid] = ws
        logging.debug('registered socket %s', sid)
        return sid

    def unregister(self, sid):
        del self.sockets[sid]
        logging.debug('unregistered socket %s', sid)
