from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QCheckBox, QPushButton


class LayoutSetting(QWidget):
    def __init__(self, overlay_window, config):
        super().__init__()

        self.running = False

        self.overlay_window = overlay_window

        player_center_checkbox = QCheckBox('以玩家为中心')
        player_center_checkbox.setChecked(config.player_center)

        # 窗口尺寸滑块
        map_size_slider_label = QLabel('窗口尺寸')
        map_size_slider = QSlider()
        map_size_slider.setOrientation(1)  # 设置为垂直方向
        map_size_slider.setMinimum(10)
        map_size_slider.setMaximum(80)
        map_size_slider.setValue(config.map_size)

        map_size_slider.valueChanged.connect(lambda value: self.update_map_size(value))

        # 窗口位置X
        map_pos_x_label = QLabel('窗口横向位移')
        map_pos_x_slider = QSlider()
        map_pos_x_slider.setOrientation(1)  # 设置为垂直方向
        map_pos_x_slider.setMinimum(-3440)
        map_pos_x_slider.setMaximum(0)
        map_pos_x_slider.setValue(-config.x)

        map_pos_x_slider.valueChanged.connect(lambda value: self.update_map_position(value, map_pos_y_slider.value()))

        # 窗口位置Y
        map_pos_y_label = QLabel('窗口照纵向位移')
        map_pos_y_slider = QSlider()
        map_pos_y_slider.setOrientation(1)  # 设置为垂直方向
        map_pos_y_slider.setMinimum(0)
        map_pos_y_slider.setMaximum(1440)
        map_pos_y_slider.setValue(config.y)

        map_pos_y_slider.valueChanged.connect(lambda value: self.update_map_position(map_pos_x_slider.value(), value))

        # 放大倍数滑块
        zoom_slider_label = QLabel('地图放大倍数: {}'.format(1))
        zoom_slider = QSlider()
        zoom_slider.setOrientation(1)  # 设置为垂直方向
        zoom_slider.setMinimum(1)
        zoom_slider.setMaximum(10)
        zoom_slider.setValue(config.zoom)

        zoom_slider.valueChanged.connect(lambda value: zoom_slider_label.setText('地图放大倍数: {}'.format(value)))

        self.preview_button = QPushButton('预览')
        self.preview_button.clicked.connect(self.preview_map)

        self.cancel_preview_button = QPushButton('取消预览')
        self.cancel_preview_button.clicked.connect(self.cancel_preview_map)
        self.cancel_preview_button.hide()

        # save_button = QPushButton('保存')
        # save_button.clicked.connect(config.write_config_to_file())

        # 创建复选框
        # checkbox_label = QLabel('Checkbox')
        # checkbox = QCheckBox('Check me')

        # 创建文本框
        # text_label = QLabel('Text')
        # text_edit = QLineEdit()

        # 创建单选按钮
        # radio_label = QLabel('Radio Buttons')
        # radio_button1 = QRadioButton('Option 1')
        # radio_button2 = QRadioButton('Option 2')
        # radio_button3 = QRadioButton('Option 3')

        # 创建垂直布局，并将小部件添加到布局中
        layout = QVBoxLayout()
        layout.addWidget(player_center_checkbox)
        layout.addWidget(map_size_slider_label)
        layout.addWidget(map_size_slider)

        layout.addWidget(map_pos_x_label)
        layout.addWidget(map_pos_x_slider)

        layout.addWidget(map_pos_y_label)
        layout.addWidget(map_pos_y_slider)

        layout.addWidget(zoom_slider_label)
        layout.addWidget(zoom_slider)

        layout.addWidget(self.preview_button)
        layout.addWidget(self.cancel_preview_button)

        # layout.addWidget(checkbox)
        # layout.addWidget(text_label)
        # layout.addWidget(text_edit)
        # layout.addWidget(radio_label)
        # layout.addWidget(radio_button1)
        # layout.addWidget(radio_button2)
        # layout.addWidget(radio_button3)

        self.setLayout(layout)

    def preview_map(self):
        self.preview_button.hide()
        self.cancel_preview_button.show()
        self.overlay_window.preview_map()
        pass

    def cancel_preview_map(self):
        self.preview_button.show()
        self.cancel_preview_button.hide()
        self.overlay_window.deactivate_preview()
        pass

    def update_map_size(self, value):
        value = 0.05 * value
        self.overlay_window.update_map_size(value)

    def update_map_position(self, x, y):
        self.overlay_window.update_map_position(-x, y)

    def deactivate_preview(self):
        self.running = True
        self.preview_button.hide()

    def activate_preview(self):
        self.running = False
        self.preview_button.show()
