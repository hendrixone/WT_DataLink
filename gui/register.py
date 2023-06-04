from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLineEdit, QPushButton, QVBoxLayout, QWidget, \
    QTextEdit

from overlay import overlay_window


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

        self.button1 = QPushButton("注册")
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
                    self.log(f"连接失败：{result}")
                    return
            except Exception as e:
                print("连接失败：", str(e))
                self.log(f"连接失败：{str(e)}")
                return
            print('连接成功')
            if self.service.register(username):
                print(f'{username} 可用')
                self.log(f'{username} 可用')
            else:
                print(f'{username} 已经被占用啦！')
                self.log(f'{username} 已经被占用啦！')
                self.service.stop()
                return
            self.service.start_listen()
            self.stacked_widget.setCurrentIndex(1)
            self.stacked_widget.currentWidget().stop_event.clear()
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
