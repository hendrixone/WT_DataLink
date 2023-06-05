import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QToolBar

from gui.dashboard import DashboardPage
from gui.register import RegisterPage
from gui.setting import Setting


def start(service):
    app = QApplication(sys.argv)
    main_window = MainWindow(service)
    sys.exit(app.exec_())


class MainWindow(QMainWindow):
    toolbar_toggle_signal = pyqtSignal(bool)

    def __init__(self, service, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Set the title for the main window
        self.setWindowTitle("WT DataLink")

        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        self.toolbar.hide()

        self.toolbar_toggle_signal.connect(self.toolbar.setVisible)

        # create actions for toolbar
        self.dashboard_action = self.toolbar.addAction("主界面")
        self.dashboard_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.dashboard_page))

        self.settings_action = self.toolbar.addAction("设置")
        self.settings_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.settings_page))

        self.stacked_widget = QStackedWidget()

        self.dashboard_page = DashboardPage(service, self.stacked_widget, main_window=self)
        self.register_page = RegisterPage(service, self.dashboard_page,
                                          stacked_widget=self.stacked_widget, main_window=self)
        self.settings_page = Setting()

        self.stacked_widget.addWidget(self.register_page)
        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.settings_page)

        self.setCentralWidget(self.stacked_widget)

        self.show()

    def closeEvent(self, event):
        self.dashboard_page.stop_all_thread()  # 停止线程
        event.accept()
        print('关闭主窗口')
        self.dashboard_page.close()
        self.register_page.close()

    def set_toolbars_visibility(self, flag):
        self.toolbar_toggle_signal.emit(flag)

    def __set_toolbars_visibility__(self, flag):
        if flag:
            self.toolbar.show()
        else:
            self.toolbar.hide()
