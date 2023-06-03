import math
import random
import socket
import sys
import threading
import time
from json import JSONDecodeError

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QLineEdit, QPushButton, QVBoxLayout, QWidget, \
    QTextEdit, QLabel

from overlay import overlay_window

from wt_port_reader import data_collector

width, height = 300, 400


def start(service):
    app = QApplication(sys.argv)
    main_window = MainWindow(service)
    sys.exit(app.exec_())


class MainWindow(QMainWindow):
    def __init__(self, service, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.stacked_widget = QStackedWidget()

        self.dashboard_page = DashboardPage(service)
        self.register_page = RegisterPage(service, self.dashboard_page, stacked_widget=self.stacked_widget)

        self.stacked_widget.addWidget(self.register_page)
        self.stacked_widget.addWidget(self.dashboard_page)

        self.setCentralWidget(self.stacked_widget)

        self.show()

    def closeEvent(self, event):
        self.dashboard_page.stop_all_thread()  # 停止线程
        event.accept()
        print('关闭主窗口')
        self.dashboard_page.close()
        self.register_page.close()


class RegisterPage(QWidget):
    update_log_signal = pyqtSignal(str)

    def __init__(self, service, dashboard, stacked_widget):
        super().__init__()

        self.overlay_window = None
        self.service = service
        self.stacked_widget = stacked_widget
        self.dashboard = dashboard

        self.username_textbox = QLineEdit()
        self.username_textbox.setText("player 1")

        self.button1 = QPushButton("Register")
        self.button1.clicked.connect(self.register)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.update_log_signal.connect(self.__update_log__)

        layout = QVBoxLayout()
        layout.addWidget(self.username_textbox)
        layout.addWidget(self.button1)
        layout.addWidget(self.log_text)
        self.setLayout(layout)

    def register(self):
        username = self.username_textbox.text()

        # Start the overlay window
        try:
            self.overlay_window = overlay_window.OverlayWindow()
            self.dashboard.overlay = self.overlay_window
        except Exception as e:
            print(e)
            self.log(str(e))
            return

        try:
            print('正在连接服务器。。。')
            try:
                result = self.service.start()
                if result is not True:
                    print("连接失败：", result)
                    return
            except Exception as e:
                print("连接失败：", str(e))
                return
            print('连接成功')
            if self.service.register(username):
                print(f'{username} 可用')
            else:
                print(f'{username} 已经被占用啦！')
                self.service.stop()
                return
            self.service.start_listen()
            self.stacked_widget.setCurrentIndex(1)
            self.stacked_widget.currentWidget().start()
        except Exception as e:
            print(e)
            self.service.stop()

    def __update_log__(self, log):
        self.log_text.append(log)

    def log(self, log):
        self.update_log_signal.emit(log)

    def closeEvent(self, event):
        print('关闭注册窗口')


class DashboardPage(QWidget):
    update_log_signal = pyqtSignal(str)
    set_lag_signal = pyqtSignal(float)

    stop_event = threading.Event()

    def __init__(self, service):
        super().__init__()
        self.service = service
        self.overlay = None

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)

        self.status_text = QLabel()
        self.latency_text = QLabel()

        self.return_button = QPushButton("Return")
        self.return_button.clicked.connect(self.return_to_register_page)

        layout = QVBoxLayout()
        layout.addWidget(self.status_text)
        layout.addWidget(self.log_text)
        self.setLayout(layout)

        self.post_data_thread = threading.Thread(target=self.start_posting_data)
        self.heartbeat_thread = threading.Thread(target=self.heartbeat)

        # Update qt using signal rather than direct call
        self.update_log_signal.connect(self.__update_log__)
        self.set_lag_signal.connect(self.__set_latency__)

    def set_status(self, status):
        self.status_text.setText(status)

    def __set_latency__(self, lag):
        lag_string = f'延迟：{lag}ms'
        self.latency_text.setText(lag_string)

    def set_latency(self, lag):
        self.set_lag_signal.emit(lag)

    def __update_log__(self, log):
        self.log_text.append(log)

    def log(self, log):
        self.update_log_signal.emit(log)

    def return_to_register_page(self):
        pass

    def stop_all_thread(self):
        self.stop_event.set()  # 设置stop_event，使得线程退出循环
        self.service.stop()
        self.post_data_thread.join()  # 等待post_data_thread线程结束
        self.heartbeat_thread.join()  # 等待heartbeat_thread线程结束
        pass

    def start(self):
        self.log(f"成功注册为 {self.service.username}")
        self.log(f"开始监听服务器数据")
        # self.local_server.start()
        self.heartbeat_thread.start()
        self.service.start_listen()
        print('开始接收服务器数据')
        self.start_posting_data_thread()
        print('开始发送数据')

    def heartbeat(self):
        counter = 0
        while not self.stop_event.is_set():
            if counter == 5:
                self.service.keep_alive()
                counter = 0
            time.sleep(0.5)
            counter += 1

    def start_posting_data_thread(self):
        self.post_data_thread.start()

    def start_posting_data(self):
        while not self.stop_event.is_set():
            start_time = time.time()

            game_status = data_collector.get_game_status()
            if game_status == data_collector.GameStatus.RUNNING:
                self.set_status('正常运行')
            elif game_status == data_collector.GameStatus.NOT_RUNNING:
                self.set_status('游戏未启动')
                self.overlay.draw_player({})
                continue
            elif game_status == data_collector.GameStatus.MENU:
                self.set_status('未在对局')
                self.overlay.draw_player({})
                continue
            elif game_status == data_collector.GameStatus.LOADING:
                self.set_status('正在加载')
                self.overlay.draw_player({})
                continue
            elif game_status == data_collector.GameStatus.NOT_SPAWNED:
                self.set_status('玩家载具未出生')
                continue
            data = data_collector.get_simple_data()
            data = {'status': data, 'username': self.service.username, 'type': 'update_status'}
            # print(data)
            self.service.send_status(data)

            players = self.service.get_data()
            players[self.service.username] = data['status']

            for player in players:
                if player == self.service.username:
                    players[player]['type'] = 'player'
                    continue
                else:
                    players[player]['type'] = 'teammate'

            self.draw_data(players)

            time.sleep(0.10)

            self.set_latency(time.time() - start_time)

    def draw_data(self, players):
        self.overlay.draw_player(players)

    def closeEvent(self, event):
        print('关闭窗口')
        self.overlay.close()

