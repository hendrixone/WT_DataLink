import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication

import service

width, height = 300, 400


class MainWindow():
    def __init__(self, service):
        self.service = service
        app = QApplication(sys.argv)
        self.window = QtWidgets.QMainWindow()
        self.window.setWindowTitle('数据链')
        # fixed size
        self.window.setFixedSize(width, height)

        # text box for username
        self.username_textbox = QtWidgets.QLineEdit("Player 1", self.window)
        self.button = QtWidgets.QPushButton("开始监听端口")

        # check available upon button click
        self.button.clicked.connect(self.listen)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.username_textbox)
        layout.addWidget(self.button)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)

        self.window.setCentralWidget(widget)

        self.window.show()

        sys.exit(app.exec_())

    def listen(self):
        print('listening')
        username = self.username_textbox.text()
        try:
            print(self.service.check_available(username))
        except Exception as e:
            print(e)





