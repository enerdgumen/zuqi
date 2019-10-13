import logging
from aiohttp import web
from conductor.config import log_level, port
from conductor.network import Network


async def network_handler(network, message):
    logging.info('received %s from %s', message.payload, message.source)
    await network.send(message.source, 'OK')
    await network.publish(message.payload)


def application(handler):
    async def shutdown(_app):
        await network.close()

    network = Network(handler=handler)
    app = web.Application()
    app.on_shutdown.append(shutdown)
    app.add_routes([web.get('/', network)])
    return app


def serve():
    logging.basicConfig(level=log_level)
    logging.info('starting conductor on port %s', port)
    web.run_app(application(network_handler), port=port)


if __name__ == '__main__':
    serve()
