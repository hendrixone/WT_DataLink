import socket
import sys
import threading
import time
from json import JSONDecodeError

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QLineEdit, QPushButton, QVBoxLayout, QWidget, \
    QTextEdit, QLabel

from map_server import LocalServer

from wt_port_reader import data_collector

width, height = 300, 400


def start(service):
    app = QApplication(sys.argv)
    window = MainWindow(service)
    sys.exit(app.exec_())


class MainWindow(QMainWindow):
    def __init__(self, service, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.service = service

        self.stacked_widget = QStackedWidget()

        self.register_page = RegisterPage(service, stacked_widget=self.stacked_widget)
        self.dashboard_page = DashboardPage(service, stacked_widget=self.stacked_widget, register_page=self.register_page)

        self.stacked_widget.addWidget(self.register_page)
        self.stacked_widget.addWidget(self.dashboard_page)

        self.setCentralWidget(self.stacked_widget)

        self.show()


class RegisterPage(QWidget):

    def __init__(self, service, stacked_widget):
        super().__init__()

        self.service = service
        self.stacked_widget = stacked_widget

        self.username_textbox = QLineEdit()
        self.username_textbox.setText("player 1")

        self.button1 = QPushButton("Register")
        self.button1.clicked.connect(self.register)
        self.log_text = QTextEdit()

        layout = QVBoxLayout()
        layout.addWidget(self.username_textbox)
        layout.addWidget(self.button1)
        layout.addWidget(self.log_text)
        self.setLayout(layout)

    def register(self):
        username = self.username_textbox.text()
        try:
            self.log_text.append('establishing connection to server')
            try:
                result = self.service.start()
                if result is not True:
                    self.log_text.append(result)
                    return
            except Exception as e:
                self.log_text.append(str(e))
                return
            self.log_text.append('connection established!')
            self.log_text.append(f'registering {username}')
            if self.service.register(username):
                self.log_text.append(f'{username} available')
            else:
                self.log_text.append(f'{username} already registered')
                self.service.stop()
                return
            self.log_text.append('switching to dashboard page')
            self.stacked_widget.setCurrentIndex(1)
            self.stacked_widget.currentWidget().start()
        except Exception as e:
            print(e)
            self.service.stop()
            self.log_text.append(str(e))


class DashboardPage(QWidget):
    update_log_signal = pyqtSignal(str)

    def __init__(self, service, stacked_widget, register_page):
        super().__init__()
        self.service = service
        self.register_page = register_page

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)

        self.status_text = QLabel()

        self.return_button = QPushButton("Return")
        self.return_button.clicked.connect(self.return_to_register_page)

        layout = QVBoxLayout()
        layout.addWidget(self.status_text)
        layout.addWidget(self.log_text)
        self.setLayout(layout)

        self.local_server = LocalServer(service, self)
        self.post_data_thread = threading.Thread(target=self.start_posting_data)
        self.heartbeat_thread = threading.Thread(target=self.heartbeat)

        # Update qt using signal rather than direct call
        self.update_log_signal.connect(self.update_log)

    def set_status(self, status):
        self.status_text.setText(status)
    def update_log(self, log):
        self.log_text.append(log)

    def log(self, log):
        self.update_log_signal.emit(log)

    def return_to_register_page(self):
        # TODO terminate all threads
        pass

    def stop_all_thread(self):
        # TODO
        pass

    def start(self):
        self.log_text.setText(self.register_page.log_text.toPlainText())
        self.local_server.start()
        self.heartbeat_thread.start()
        self.log('local service started on localhost:8222')
        self.set_status('启动成功, 浏览器访问localhost:8222')

    def heartbeat(self):
        while True:
            self.service.keep_alive()
            time.sleep(5)

    def start_posting_data_thread(self):
        self.post_data_thread.start()

    def start_posting_data(self):
        self.log("Starting to post data")
        while True:
            start_time = time.time()
            time.sleep(0.25)
            try:
                status = data_collector.get_simple_data()
                data = {'status': status, 'username': self.service.username, 'type': 'update_status'}
                print(data)
                self.service.send_status(data)
            except socket.timeout:
                self.log("Time out, Check is WarThunder running")
                self.set_status('连接失败, 请检查游戏是否启动')
            except JSONDecodeError:
                self.log("Not in active game session")
                self.set_status('不在飞行状态')
            except Exception as e:
                self.log(str(e))
                self.set_status("您电脑开了吗？")
            self.set_status(f'更新成功, 耗时{time.time() - start_time:.2f}秒')



    def start_receiving_data(self):
        self.log("Starting to recieve data")
        while True:
            data = self.service.get_data()
            self.log(data)
            time.sleep(0.25)
