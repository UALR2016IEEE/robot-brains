import multiprocessing.connection


class IOHandler(object):
    def __init__(self):
        self.host, self.port = 'localhost', 9998
        self.client = None
        self.halt = False

    def start(self, host, port):
        self.halt = False
        self.host, self.port = host, port
        self.client = multiprocessing.connection.Client((self.host, self.port))

    def stop(self):
        self.halt = True
        self.client.close()

    def send_data(self, item):
        if self.client is not None:
            self.client.send(item)
