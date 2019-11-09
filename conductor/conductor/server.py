import logging
from aiohttp import web

from conductor.game import Conductor
from conductor.config import log_level, port
from conductor.network import Network
from conductor.quiz import OpenTriviaQuizSource


def application(network, shutdown):
    app = web.Application()
    app.on_shutdown.append(shutdown)
    app.add_routes([web.get('/', network)])
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
