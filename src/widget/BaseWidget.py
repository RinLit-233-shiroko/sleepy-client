from PyQt5 import uic
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QSizePolicy, QHBoxLayout, QVBoxLayout
from qfluentwidgets import FluentIcon as fIcon, StrongBodyLabel, TransparentDropDownToolButton, \
    IconWidget, RoundMenu, Action, ImageLabel, CardWidget

from src import config as cf
from src.widget.Setting import base_widget_layout


class BaseWidget(CardWidget):
    def __init__(self, parent=None, title='基本组件',
                 icon=fIcon.LIBRARY_FILL.colored(QColor('#666'), QColor('#CCC')) or '',
                 layout=None,
                 ):
        super().__init__(parent)
        uic.loadUi(base_widget_layout, self)

        self.parent = parent
        self.layout = layout
        self.more_options_menu = None
        self.title_label = None
        self.icon_label = None
        self.more_options = None
        self.top_layout = None
        self.bottom_layout = None
        self.content_layout = None
        self.title = title
        self.icon = icon
        self.width_threshold = 500  # 设置宽度阈值

        self.initUi()

        self.setMinimumWidth(250)
        self.setMinimumHeight(250)
        self.setMaximumWidth(500)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def initUi(self):
        self.top_layout = self.findChild(QHBoxLayout, 'top')
        self.bottom_layout = self.findChild(QHBoxLayout, 'bottom')
        self.content_layout = self.findChild(QVBoxLayout, 'content')

        self.title_label = self.findChild(StrongBodyLabel, 'title_label')
        self.more_options = self.findChild(TransparentDropDownToolButton, 'more_options')

        if type(self.icon) is str:
            self.icon_label = ImageLabel()
            self.icon_label.setImage(self.icon)
        else:
            self.icon_label = IconWidget()
            self.icon_label.setIcon(self.icon)

        self.more_options_menu = RoundMenu(self)
        self.more_options_menu.addAction(Action(fIcon.CLOSE, '移除本组件', triggered=self.remove_widget))

        self.title_label.setText(self.title)
        self.more_options.setFixedSize(36, 30)
        self.icon_label.setFixedSize(18, 18)

        self.more_options.setMenu(self.more_options_menu)

        self.top_layout.insertWidget(0, self.icon_label)

    def hide_title(self):
        self.title_label.hide()
        self.icon_label.hide()

    def remove_widget(self):
        from src.widget.Utils import widgets_config, find_key

        widget = find_key(widgets_config, self.__class__)
        cf.widgets_config.remove(widget)
        self.parent.add_widgets()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        new_width = event.size().width()
        if new_width > self.width_threshold:
            self.setMinimumHeight(300)  # 当宽度超过阈值时，设置新的最小高度
        else:
            self.setMinimumHeight(250)  # 当宽度未超过阈值时，恢复原来的最小高度
