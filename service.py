import requests

class Service:
    def __init__(self, ip, port, protocol):
        self.ip = ip
        self.port = port
        self.protocol = protocol
        self.url = f'{protocol}://{ip}:{port}'
        self.username = None

    def check_available(self, username):
        # set timeout
        try:
            # send request to server using username as parameter
            response = requests.get(f'{self.url}', params={'username': username}, timeout=200)
            # if response is ok, return true
            if response.ok:
                return True
            # else return the server response as json
            else:
                return response.json()
        except Exception as e:
            return e

    def register(self, username):
        try:
            response = requests.post(f'{self.url}/register', params={'username': username, 'register': True})
            if response.ok:
                self.username = username
                return True
            else:
                return response.json()
        except Exception as e:
            return e

    # refresh every 10 seconds, otherwise the client is considered offline
    def keep_wake(self):
        try:
            response = requests.post(f'{self.url}/keep_wake', params={'username': self.username})
            if response.ok:
                return True
            else:
                return response.json()
        except Exception as e:
            return e

    def send_status(self, status):
        try:
            # send status in request body
            response = requests.post(f'{self.url}/post_data', params={'username': self.username}, json=status)
            if response.ok:
                return True
            else:
                return response.json()
        except Exception as e:
            return e

    def get_status(self):
        try:
            response = requests.get(f'{self.url}/get_data', params={'username': self.username})
            if response.ok:
                return response.json()
            else:
                return response.json()
        except Exception as e:
            return e