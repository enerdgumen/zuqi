import asyncio
import logging
from aiohttp import web
from box import Box

from conductor.game import Conductor
from conductor.config import log_level, port
from conductor.network import Network


def application(network):
    async def shutdown(_app):
        await network.close()

    app = web.Application()
    app.on_shutdown.append(shutdown)
    app.add_routes([web.get('/', network)])
    return app


class MockQuizSource:
    async def next(self):
        return Box(question='2+1?', answers=['1', '2', '3', '4'], answer=2)


def serve():
    logging.basicConfig(level=log_level)
    logging.info('starting conductor on port %s', port)
    conductor = Conductor(quiz_source=MockQuizSource())
    network = Network(
        on_enter=conductor.on_enter,
        on_message=conductor.on_message,
        on_exit=conductor.on_exit
    )
    web.run_app(application(network), port=port)


if __name__ == '__main__':
    serve()
