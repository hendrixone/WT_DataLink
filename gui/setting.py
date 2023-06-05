from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QCheckBox, QLineEdit, QRadioButton, QPushButton


class Setting(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Settings')
        self.setGeometry(100, 100, 300, 200)

        in_game_map_checkbox = QCheckBox('开启游戏内地图')
        in_game_hmd_checkbox = QCheckBox('开启HMD（需要使用头瞄软件） 未实现')

        # 窗口尺寸滑块
        map_size_slider_label = QLabel('窗口尺寸: {}'.format(20))
        map_size_slider = QSlider()
        map_size_slider.setOrientation(1)  # 设置为垂直方向
        map_size_slider.setMinimum(10)
        map_size_slider.setMaximum(50)
        map_size_slider.setValue(20)

        map_size_slider.valueChanged.connect(lambda value: map_size_slider_label.setText('窗口尺寸: {}'.format(value)))

        # 放大倍数滑块
        zoom_slider_label = QLabel('地图放大倍数: {}'.format(1))
        zoom_slider = QSlider()
        zoom_slider.setOrientation(1)  # 设置为垂直方向
        zoom_slider.setMinimum(1)
        zoom_slider.setMaximum(10)
        zoom_slider.setValue(1)

        zoom_slider.valueChanged.connect(lambda value: zoom_slider_label.setText('地图放大倍数: {}'.format(value)))

        save_button = QPushButton('保存')
        save_button.clicked.connect(self.save)

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
        layout.addWidget(in_game_map_checkbox)
        layout.addWidget(in_game_hmd_checkbox)
        layout.addWidget(map_size_slider_label)
        layout.addWidget(map_size_slider)
        layout.addWidget(zoom_slider_label)
        layout.addWidget(zoom_slider)

        # layout.addWidget(checkbox)
        # layout.addWidget(text_label)
        # layout.addWidget(text_edit)
        # layout.addWidget(radio_label)
        # layout.addWidget(radio_button1)
        # layout.addWidget(radio_button2)
        # layout.addWidget(radio_button3)

        self.setLayout(layout)
        self.show()

    def save(self):
        print('保存')
        # self.close()