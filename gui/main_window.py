import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QToolBar

from gui.dashboard import DashboardPage
from gui.register import RegisterPage

# Update interval
UPDATE_INTERVAL = 0.1


def start(service):
    app = QApplication(sys.argv)
    main_window = MainWindow(service)
    sys.exit(app.exec_())


class MainWindow(QMainWindow):
    def __init__(self, service, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Set the title for the main window
        self.settings_page = None
        self.setWindowTitle("WT DataLink")

        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        # create actions for toolbar
        self.dashboard_action = self.toolbar.addAction("Dashboard")
        self.dashboard_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.dashboard_page))

        self.settings_action = self.toolbar.addAction("Settings")
        self.settings_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.settings_page))

        self.stacked_widget = QStackedWidget()

        self.dashboard_page = DashboardPage(service, self.stacked_widget)
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

