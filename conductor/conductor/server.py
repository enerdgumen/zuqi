import logging
from aiohttp import web
from conductor.config import log_level, port
from conductor.network import Network


def application(network):
    async def shutdown(_app):
        await network.close()

    app = web.Application()
    app.on_shutdown.append(shutdown)
    app.add_routes([web.get('/', network)])
    return app


def serve():
    async def on_enter(_network, user):
        logging.info('entered user %s', user)

    async def on_message(network, message):
        logging.info('received %s from %s', message.payload, message.source)
        await network.send(message.source, 'OK')
        await network.publish(message.payload)

    async def on_exit(_network, user):
        logging.info('exit user %s', user)

    logging.basicConfig(level=log_level)
    logging.info('starting conductor on port %s', port)
    network = Network(on_enter=on_enter, on_message=on_message, on_exit=on_exit)
    web.run_app(application(network), port=port)


if __name__ == '__main__':
    serve()
