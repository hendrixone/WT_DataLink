import threading
import time

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QTextEdit, QLabel, QPushButton, QVBoxLayout, QWidget

from wt_port_reader import data_collector


class DashboardPage(QWidget):
    update_log_signal = pyqtSignal(str)
    set_lag_signal = pyqtSignal(float)

    stop_event = threading.Event()

    def __init__(self, service, stacked_widget):
        super().__init__()
        self.lag_list = []
        self.service = service
        self.overlay = None
        self.stacked_widget = stacked_widget

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)

        self.status_text = QLabel()
        self.latency_text = QLabel()

        self.return_button = QPushButton("终止")
        self.return_button.clicked.connect(self.return_to_register_page)

        layout = QVBoxLayout()
        layout.addWidget(self.status_text)
        layout.addWidget(self.latency_text)
        layout.addWidget(self.log_text)
        layout.addWidget(self.return_button)
        self.setLayout(layout)

        self.post_data_thread = None
        self.heartbeat_thread = None

        # Update qt using signal rather than direct call
        self.update_log_signal.connect(self.__update_log__)
        self.set_lag_signal.connect(self.__set_latency__)

    def set_status(self, status):
        self.status_text.setText(status)

    def __set_latency__(self, lag):
        self.lag_list.append(lag)
        if len(self.lag_list) > 5:
            self.lag_list.pop(0)
            lag_string = f'延迟：{sum(self.lag_list) / 5}ms'
            self.latency_text.setText(lag_string)

    def set_latency(self, lag):
        self.set_lag_signal.emit(lag)

    def __update_log__(self, log):
        self.log_text.append(log)

    def log(self, log):
        self.update_log_signal.emit(log)

    def return_to_register_page(self):
        self.stop_all_thread()
        self.stacked_widget.setCurrentIndex(0)
        pass

    def stop_all_thread(self):
        self.stop_event.set()  # 设置stop_event，使得线程退出循环
        self.service.stop()
        self.post_data_thread.join()  # 等待post_data_thread线程结束
        self.heartbeat_thread.join()  # 等待heartbeat_thread线程结束
        self.overlay.activated = False
        self.overlay.update()
        pass

    def start(self):
        self.log(f"成功注册为 {self.service.username}")
        self.log(f"开始运行")
        # self.local_server.start()
        self.heartbeat_thread = threading.Thread(target=self.heartbeat)
        self.heartbeat_thread.start()
        self.service.start_listen()
        print('开始接收服务器数据')
        self.post_data_thread = threading.Thread(target=self.start_posting_data)
        self.post_data_thread.start()
        print('开始发送数据')

    def heartbeat(self):
        counter = 0
        while not self.stop_event.is_set():
            if counter == 5:
                self.service.keep_alive()
                counter = 0
            time.sleep(0.5)
            counter += 1

    def start_posting_data(self):
        while not self.stop_event.is_set():
            start_time = time.time()

            game_status = data_collector.get_game_status()
            if game_status == data_collector.GameStatus.RUNNING:
                self.set_status('正常运行')
            elif game_status == data_collector.GameStatus.NOT_RUNNING:
                self.set_status('游戏未启动')
                self.overlay.activated = False
                continue
            elif game_status == data_collector.GameStatus.MENU:
                self.set_status('未在对局')
                self.overlay.activated = False
                continue
            elif game_status == data_collector.GameStatus.LOADING:
                self.set_status('正在加载')
                self.overlay.activated = False
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

            self.overlay.activated = True

            self.draw_data(players)

            time_to_sleep = UPDATE_INTERVAL - (time.time() - start_time)

            if time_to_sleep > 0:
                time.sleep(time_to_sleep)

            self.set_latency(time.time() - start_time)

    def draw_data(self, players):
        self.overlay.draw_player(players)

    def closeEvent(self, event):
        print('关闭窗口')
        self.overlay.close()