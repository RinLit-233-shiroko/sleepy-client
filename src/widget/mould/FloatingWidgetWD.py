from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor
from qfluentwidgets import isDarkTheme

from src.widget.Setting import window_detection_widget_icon
from src.widget.mould.WindowDetectionWidget import WindowDetectionWidget


class FloatingWidgetWD(WindowDetectionWidget):
    def __init__(self, parent=None):
        super().__init__(parent=None, layout=None)
        self.parent = parent  # 父窗口
        self.parent.showMinimized()  # 最小化父窗口
        self.offset = None
        self.dragging = False

        self.more_options.hide()

        self.floating_widget_button.clicked.disconnect()
        self.floating_widget_button.clicked.connect(self.close)

    def initUi(self):
        super().initUi()
        self.setWindowTitle('窗口检测')
        self.setWindowIcon(QIcon(window_detection_widget_icon))
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)  # 作为工具窗口防Alt+Tab()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(300, 200)

    def closeEvent(self, event):
        event.accept()
        self.parent.showNormal()  # 显示父窗口
        if self.is_listening:
            self.start_listen()

    # 颜色
    def _normalBackgroundColor(self):  # DARK -> LIGHT
        return QColor(37, 37, 38, 230) if isDarkTheme() else QColor(255, 255, 255, 230)

    def _hoverBackgroundColor(self):
        return QColor(37, 37, 38, 252) if isDarkTheme() else QColor(255, 255, 255, 252)

    def _pressedBackgroundColor(self):
        return QColor(37, 37, 38, 215) if isDarkTheme() else QColor(255, 255, 255, 215)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self.dragging:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            self.dragging = False

