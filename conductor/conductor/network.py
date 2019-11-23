import asyncio
from collections import namedtuple
import logging

from aiohttp import WSMsgType, web
from box import Box
from cerberus import Validator

Message = namedtuple('Message', ['user', 'body'])


async def noop(*_args):
    pass


class Network:
    request_schema = {
        'uid': {
            'type': 'string',
            'empty': False
        }
    }

    def __init__(self, registry, on_enter=noop, on_message=noop, on_exit=noop):
        self.registry = registry
        self.on_enter = on_enter
        self.on_message = on_message
        self.on_exit = on_exit

    async def __call__(self, request):
        user = self._read_user(request)
        ws = web.WebSocketResponse()
        ws_ready = ws.can_prepare(request)
        if not ws_ready.ok:
            raise web.HTTPMethodNotAllowed()
        await ws.prepare(request)
        error = self.registry.register(ws, user)
        if error:
            await ws.send_json(Box(event='rejected', reason=error))
            return ws
        await ws.send_json(Box(event='ready'))
        await self.on_enter(self, user)
        try:
            await self._listen_messages(user, ws)
        finally:
            self.registry.unregister(user)
            await self.on_exit(self, user)
        return ws

    def _read_user(self, request):
        query = Box(request.query)
        validator = Validator(self.request_schema)
        if not validator.validate(query):
            raise web.HTTPBadRequest()
        return query.uid

    async def _listen_messages(self, user, ws):
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
        await asyncio.gather(*[ws.send_json(body) for ws in self.registry.sockets.values()])

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
