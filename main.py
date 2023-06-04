import queue
import threading
import time

from gui import main_window
import service
from overlay import overlay_window

local = "127.0.0.1"
remote = "124.221.106.45"
mac = "192.168.31.137"
port = 8221

if __name__ == '__main__':
    service = service.ServerService(host=remote, port=port)
    main_window.start(service)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
