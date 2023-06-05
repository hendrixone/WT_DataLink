import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QToolBar

from gui.dashboard import DashboardPage
from gui.layout import LayoutSetting
from gui.register import RegisterPage
from gui.setting import Setting
from overlay.overlay_window import OverlayWindow
from utils.config import Config


def start(service):
    config = Config()

    app = QApplication(sys.argv)
    overlay_window = OverlayWindow(config)
    MainWindow(service, overlay_window, config)
    sys.exit(app.exec_())


class MainWindow(QMainWindow):
    toolbar_toggle_signal = pyqtSignal(bool)

    def __init__(self, service, overlay, config, *args, **kwargs):
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

        self.layout_settings_action = self.toolbar.addAction("布局设置")
        self.layout_settings_action.triggered.connect(
            lambda: self.stacked_widget.setCurrentWidget(self.layout_settings_page))

        self.stacked_widget = QStackedWidget()

        self.dashboard_page = DashboardPage(service, self.stacked_widget, main_window=self, overlay=overlay)
        self.register_page = RegisterPage(service, self.dashboard_page,
                                          stacked_widget=self.stacked_widget, main_window=self, overlay=overlay)
        self.settings_page = Setting()
        self.layout_settings_page = LayoutSetting(overlay_window=overlay, config=config)

        self.stacked_widget.addWidget(self.register_page)
        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.settings_page)
        self.stacked_widget.addWidget(self.layout_settings_page)

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
