from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QPushButton


class Setting(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        in_game_map_checkbox = QCheckBox('开启游戏内地图')
        in_game_hmd_checkbox = QCheckBox('开启HMD（需要使用头瞄软件） 未实现')

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

        # layout.addWidget(checkbox)
        # layout.addWidget(text_label)
        # layout.addWidget(text_edit)
        # layout.addWidget(radio_label)
        # layout.addWidget(radio_button1)
        # layout.addWidget(radio_button2)
        # layout.addWidget(radio_button3)

        self.setLayout(layout)

    def save(self):
        # TODO: 保存设置
        print('保存')
        # self.close()
