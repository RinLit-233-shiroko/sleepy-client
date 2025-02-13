from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QSizePolicy, QSpacerItem
from loguru import logger
from qfluentwidgets import FluentIcon as fIcon, RoundMenu, Action, BodyLabel, PrimaryDropDownPushButton, SubtitleLabel, \
    InfoBarPosition, InfoBar

from src import config as cf
from src.nt_thread import getDictThread
from src.widget.BaseWidget import BaseWidget
from src.widget.Setting import status_widget_icon


class StatusWidget(BaseWidget):
    def __init__(self, parent=None, layout=None):
        super().__init__(parent=parent, layout=layout, title='切换状态', icon=status_widget_icon)
        # status = ['复活啦 ( •̀ ω •́ )✧', '似了 o(TヘTo)']
        # noinspection SpellCheckingInspection
        self.font_color = {
            'awake': (QColor('#3BB871'), QColor('#87FFBB')),
            'sleeping': (QColor('#666'), QColor('#CCC')),
        }

        self.get_json_thread = None
        self.change_status_thread = None
        menu = RoundMenu()
        # menu.addActions([
        #     Action(fIcon.CALORIES, status[0]),
        #     Action(fIcon.QUIET_HOURS, status[1])
        # ])
        for key, status in cf.status_dict.items():
            menu.addAction(Action(status, triggered=partial(self.change_status, key)))

        self.body_label = BodyLabel()
        self.status_label = SubtitleLabel()
        self.switch_button = PrimaryDropDownPushButton()

        self.body_label.setText(f'当前状态：')  # Body
        self.body_label.setAlignment(Qt.AlignCenter)
        self.status_label.setText(cf.status_info['name'])  # 状态
        self.status_label.setAlignment(Qt.AlignCenter)
        self.switch_button.setText('设置状态')

        self.switch_button.setIcon(fIcon.MESSAGE)
        self.switch_button.setMenu(menu)

        self.content_layout.addWidget(self.body_label)
        self.content_layout.addWidget(self.status_label)
        self.content_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.content_layout.addWidget(self.switch_button)

        self.get_color(cf.status_info['color'])

    def get_color(self, color_name=str):  # 获取颜色
        if color_name in self.font_color:
            self.status_label.setTextColor(self.font_color[color_name][0], self.font_color[color_name][1])
            return self.font_color[color_name]
        self.status_label.setTextColor(QColor('#666'), QColor('#CCC'))

    def get_status(self):
        def callback_status(data):
            cf.status_info = data['info']
            self.status_label.setText(cf.status_info['name'])  # 状态
            self.get_color(cf.status_info['color'])
            logger.debug(f'当前状态：{cf.status_info}')

        self.get_json_thread = getDictThread(f'{cf.server}/query')
        self.get_json_thread.json_signal.connect(callback_status)
        self.get_json_thread.start()
        logger.debug('开始获取状态信息')

    def change_status(self, status):
        def callback(data):
            # 部分源于 wyf9
            try:
                print(f'success: [{data["success"]}], code: [{data["code"]}], set_to: [{data["set_to"]}]')
                self.get_status()
                current_state = cf.status_dict[data['set_to']].split(' - ')[0]

                InfoBar.success(
                    title='更改状态成功',
                    content=f"已将状态更改为 {current_state}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self.parent
                )
            except:
                print(f'RawData: {data}')
                InfoBar.error(
                    title='更改状态失败',
                    content=f"错误代码： {data}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self.parent
                )

        self.change_status_thread = getDictThread(f'{cf.server}/set/{cf.secret}/{status}')
        self.change_status_thread.json_signal.connect(callback)
        self.change_status_thread.start()

