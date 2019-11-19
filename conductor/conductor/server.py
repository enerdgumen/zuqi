import logging
import os.path
from aiohttp import web

from conductor.game import Conductor
from conductor.config import log_level, port, static_files_path
from conductor.network import Network
from conductor.quiz import OpenTriviaQuizSource


async def index(_request):
    return web.FileResponse(os.path.join(static_files_path, 'index.html'))


def application(network, shutdown):
    app = web.Application()
    app.on_shutdown.append(shutdown)
    app.add_routes([
        web.get('/', index),
        web.get('/play', network)
    ])
    if static_files_path:
        app.add_routes([web.static('/', static_files_path)])
    return app


def serve():
    async def shutdown(_app):
        await network.close()
        await quiz_source.close()

    logging.basicConfig(level=log_level)
    logging.info('starting conductor on port %s', port)
    quiz_source = OpenTriviaQuizSource()
    conductor = Conductor(quiz_source=quiz_source)
    network = Network(
        on_enter=conductor.on_enter,
        on_message=conductor.on_message,
        on_exit=conductor.on_exit
    )
    web.run_app(application(network, shutdown), port=port)


if __name__ == '__main__':
    serve()
