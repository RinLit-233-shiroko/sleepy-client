from datetime import datetime

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from qfluentwidgets import BodyLabel, ProgressRing

from src.widget.BaseWidget import BaseWidget
from src.widget.Setting import day_progress_widget_icon


class DayProgressWidget(BaseWidget):
    def __init__(self, parent=None, layout=None):
        super().__init__(parent=parent, layout=layout, title='今日进度', icon=day_progress_widget_icon)
        self.body_label = BodyLabel()
        self.body_label.setText(f'{datetime.now().strftime("%H:%M:%S")}\n今天已经过了')
        self.body_label.setFont(QFont('Microsoft YaHei', 12))
        self.body_label.setAlignment(Qt.AlignCenter)

        self.day_progress_ring = ProgressRing()
        self.day_progress_ring.setRange(0, 100)
        self.day_progress_ring.setValue(int((datetime.now().hour * 60 + datetime.now().minute) / 14.4))
        self.day_progress_ring.setFixedSize(100, 100)
        self.day_progress_ring.setStrokeWidth(8)
        self.day_progress_ring.setStyleSheet('font-size: 16px;')
        self.day_progress_ring.setTextVisible(True)

        self.content_layout.setSpacing(22)
        self.content_layout.addWidget(self.body_label)
        self.content_layout.addWidget(self.day_progress_ring)

        self.update_timer = QTimer()
        self.update_timer.setInterval(1000)
        self.update_timer.timeout.connect(self.update_progress)
        self.update_timer.start()

    def update_progress(self):
        self.day_progress_ring.setValue(int((datetime.now().hour * 60 + datetime.now().minute) / 14.4))
        self.body_label.setText(f'{datetime.now().strftime("%H:%M:%S")}\n今天已经过了')

