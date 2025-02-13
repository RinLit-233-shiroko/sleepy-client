from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QSizePolicy, QHBoxLayout, QSpacerItem
from loguru import logger
from qfluentwidgets import FluentIcon as fIcon, BodyLabel, PrimaryPushButton, \
    InfoBarPosition, InfoBar, LineEdit, SwitchButton, TransparentToolButton

from src import config as cf
from src.nt_thread import postThread
from src.widget.BaseWidget import BaseWidget
from src.widget.Setting import RETRY, window_detection_widget_icon


class WindowDetectionWidget(BaseWidget):
    def __init__(self, parent=None, layout=None):
        super().__init__(parent=parent, layout=layout, title='窗口检测', icon=window_detection_widget_icon)
        self.retry_count = 0
        self.post_thread = None
        self.is_listening = False
        self.using_fake_window = False
        self.fake_window_name = ''

        self.floating_widget = None
        self.floating_widget_button = TransparentToolButton()
        self.window_name_layout = QHBoxLayout()
        self.window_name_label = BodyLabel()
        self.window_name = LineEdit()

        self.name_layout = QHBoxLayout()
        self.name_label = BodyLabel()
        self.name = LineEdit()

        self.fake_layout = QHBoxLayout()
        self.fake_label = BodyLabel()
        self.update_fake_window = SwitchButton()

        self.play_pause_button = PrimaryPushButton()

        self.floating_widget_button.setIcon(fIcon.MINIMIZE)
        self.floating_widget_button.clicked.connect(self.open_floating_widget)
        self.fake_label.setText('使用自定义名称：')
        self.update_fake_window.checkedChanged.connect(self.set_using_fake_window)
        self.fake_layout.addWidget(self.fake_label)
        self.fake_layout.addWidget(self.update_fake_window)

        self.name_label.setText('设备名称：')
        self.name.setText(cf.device_name)
        self.name.textChanged.connect(lambda text: cf.config.upload_config('device_name', text))
        self.name.setPlaceholderText('您的设备名称')

        self.window_name_label.setText('检测窗口：')
        self.window_name.setReadOnly(True)
        self.window_name.setPlaceholderText('检测到的窗口名称将会显示于此')
        self.window_name.textEdited.connect(self.set_fake_window)

        self.play_pause_button.setText('开始上传')
        self.play_pause_button.setIcon(fIcon.PLAY)
        self.play_pause_button.clicked.connect(self.start_listen)

        self.top_layout.insertWidget(3, self.floating_widget_button)
        self.window_name_layout.addWidget(self.window_name_label)
        self.window_name_layout.addWidget(self.window_name)
        self.name_layout.addWidget(self.name_label)
        self.name_layout.addWidget(self.name)
        self.content_layout.addLayout(self.name_layout)
        self.content_layout.addLayout(self.window_name_layout)
        self.content_layout.addLayout(self.fake_layout)
        self.content_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.content_layout.addWidget(self.play_pause_button)

        self.update_timer = QTimer()
        self.update_timer.setInterval(cf.check_interval)
        self.update_timer.timeout.connect(self.update_window)

    def open_floating_widget(self):
        from src.widget.mould.FloatingWidgetWD import FloatingWidgetWD

        floating_widget = FloatingWidgetWD(self.parent)
        floating_widget.show()

    def set_fake_window(self, text):
        self.fake_window_name = text

    def set_using_fake_window(self, checked):
        self.using_fake_window = checked
        if checked:
            self.window_name.clear()
            self.window_name.setReadOnly(False)
        else:
            self.fake_window_name = ''
            self.window_name.setReadOnly(True)
            self.window_name.clear()

    def start_listen(self):
        if not self.is_listening:
            self.update_window()
            self.play_pause_button.setText('停止上传')
            self.play_pause_button.setIcon(fIcon.PAUSE)
            self.update_timer.start()
            self.is_listening = True
            return

        self.retry_count = 0
        self.play_pause_button.setText('开始上传')
        self.play_pause_button.setIcon(fIcon.PLAY)
        # self.window_name.clear()
        self.update_timer.stop()
        self.is_listening = False

    def update_window(self):
        def callback(data):
            net_info = data[1]

            if type(net_info) is str:
                self.retry_count += 1

                logger.warning(f'上传窗口失败[{self.retry_count}/{RETRY}]：{net_info}')

                if self.retry_count > RETRY:  # 重试次数达到上限
                    logger.error(f'上传窗口失败[达到上限]：{net_info}')
                    InfoBar.error(
                        title='上传窗口失败',
                        content=f"错误信息：{net_info}",
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.BOTTOM,
                        duration=-1,
                        parent=self.parent
                    )
                    self.start_listen()  # 禁用监听
                return

            if net_info['success'] is False:
                InfoBar.error(
                    title='上传窗口失败',
                    content=f"错误信息：(code:{net_info['code']}){net_info['message']}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.BOTTOM,
                    duration=-1,
                    parent=self.parent
                )
                self.start_listen()  # 禁用监听
                return

            if self.using_fake_window:
                return
            self.window_name.setText(data[0])

        self.post_thread = postThread(self.fake_window_name)
        self.post_thread.list_signal.connect(callback)
        self.post_thread.start()
