import json
import socket
import threading

TIMEOUT = 10


class ServerService:
    def __init__(self, host, port):
        self.client_socket = None
        self.username = None
        self.host = host
        self.port = port
        self.stop_event = threading.Event()
        # message queue
        self.data = {}

    def start(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))

        return True

    def stop(self):
        self.stop_event.set()
        if self.client_socket is None:
            return
        self.client_socket.close()

    def register(self, username):
        self.__send_data__({'username': username, 'type': 'check_available'})
        data = self.client_socket.recv(1024)
        self.username = username
        received_message = json.loads(data.decode())['available']
        return received_message

    def keep_alive(self):
        self.__send_data__({'username': self.username, 'type': 'heartbeat'})

    def get_data(self):
        return self.data

    def send_status(self, status):
        try:
            self.__send_data__(status)
        except Exception as e:
            print(e)
            self.start()

    def __send_data__(self, data):
        json_data = json.dumps(data)
        # print('send: ', json_data)
        self.client_socket.sendall(json_data.encode())

    def start_listen(self):
        receive_thread = threading.Thread(target=self.__listen__)
        receive_thread.start()

    def __listen__(self):
        while not self.stop_event.is_set():
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    continue
                received_message = data.decode()
                # print('rec: ', received_message)
                if received_message == 'ok':
                    continue
                self.data = json.loads(received_message)
            except ConnectionAbortedError:
                break

    def __del__(self):
        self.stop()


if __name__ == '__main__':
    dict = {'a': {'b': 1, 'c': 2}, 'd': {'e': 3, 'f': 4}}
    for abc in dict:
        print(abc)
        print(dict[abc])
