import logging
from aiohttp import web
from conductor.config import port, log_level
from conductor.network import Network


def serve():
    async def consumer(message):
        logging.info('received %s from %s', message.payload, message.source)
        await message.reply('OK')
        await network.publish(message.payload)

    async def shutdown(_app):
        await network.close()

    logging.basicConfig(level=log_level)
    logging.info('starting conductor')
    network = Network(handler=consumer)
    app = web.Application()
    app.on_shutdown.append(shutdown)
    app.add_routes([web.get('/', network)])
    web.run_app(app, port=port)


if __name__ == '__main__':
    serve()
