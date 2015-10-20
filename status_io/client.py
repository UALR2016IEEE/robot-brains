import multiprocessing
import multiprocessing.connection
import socket
import pickle
import struct


class IOHandler(multiprocessing.Process):
    def __init__(self):
        self.halt = multiprocessing.Value('b', False)
        self.data = multiprocessing.Queue()
        multiprocessing.Process.__init__(self, target=self.io_inf, args=(self.data, self.halt))

    def start(self):
        self.halt.value = False
        super(multiprocessing.Process, self).start()

    def stop(self):
        print('stopping')
        self.halt.value = True

    def send_data(self, item):
        print('received to send', item[0])
        self.data.put(item)

    def io_inf(self, q, halt):
        host, port = 'localhost', 9998
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((host, port))
            print("connected to", host, "on", port, 'halt', halt.value)
            while not halt.value:
                while not q.empty():
                    data = q.get()
                    # print('processing queue', data)
                    packet = pickle.dumps(data, protocol=4)
                    length = struct.pack('!I', len(packet))
                    packet = length + packet
                    client.sendall(packet)
        except ConnectionError:
            print('connection error with server, closed')
            halt.value = True
        client.close()
