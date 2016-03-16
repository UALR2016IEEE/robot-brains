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

            # robot position needs converting from internal mm to pixels
            if item[0] == 'robot-pos':
                command = item[0]
                payload = item[1].mm2pix()
                item = (command, payload)

            # io.send_data(('lidar-points', (position, scan)))
            elif item[0] == 'lidar-points':
                command = item[0]
                payload = item[1]
                p = payload[0].mm2pix()
                s = payload[1]
                item = (command, (p, s))

            self.client.send(item)
