import logging


class SocketRegistry:
    def __init__(self, max_sockets):
        self.max_sockets = max_sockets
        self.sockets = {}

    def register(self, ws, uid):
        if len(self.sockets) >= self.max_sockets:
            return 'maxSocketsReached'
        if uid in self.sockets:
            return 'usernameNotAvailable'
        self.sockets[uid] = ws
        logging.debug('%s: registered socket', uid)

    def unregister(self, uid):
        del self.sockets[uid]
        logging.debug('%s: unregistered socket', uid)
