import os
import shutil

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog
from loguru import logger
from qfluentwidgets import FluentIcon as fIcon, Action, ImageLabel, BodyLabel, InfoBarPosition, InfoBar

from src.widget.BaseWidget import BaseWidget
from src.widget.Setting import photo_dir, photo_widget_icon


class PhotoWidget(BaseWidget):
    def __init__(self, parent=None, layout=None):
        super().__init__(parent=parent, layout=layout, title='照片墙', icon=photo_widget_icon)
        self.photo_label = ImageLabel()

        self.more_options_menu.addAction(Action(fIcon.ADD, '上传照片', triggered=self.upload_photo))

        self.photo_label.setImage(photo_dir)
        self.photo_label.setScaledContents(True)
        self.photo_label.scaledToWidth(self.width() - 30)
        self.photo_label.setBorderRadius(8, 8, 8, 8)

        self.tip_no_photo = BodyLabel()
        self.tip_no_photo.setText('还没有选择照片啊……\nㄟ( ▔, ▔ )ㄏ')
        self.tip_no_photo.setAlignment(Qt.AlignCenter)

        self.content_layout.setContentsMargins(0, 0, 0, 0)
        if os.path.exists(photo_dir):
            self.content_layout.addWidget(self.photo_label)
        else:
            self.content_layout.addWidget(self.tip_no_photo)

    def upload_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '上传照片', '', '图片文件 (*.jpg *.png)')
        if file_path:
            try:
                shutil.copy(file_path, photo_dir)
                self.photo_label.setImage(photo_dir)

                self.content_layout.removeWidget(self.tip_no_photo)
                self.content_layout.addWidget(self.photo_label)
            except Exception as e:
                logger.error(f'上传照片失败：{e}')
                InfoBar.error(
                    title='上传照片失败',
                    content=f"错误信息：{e}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self.parent
                )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.width() < 550:
            self.photo_label.scaledToWidth(self.width() - 30)
        else:
            self.photo_label.scaledToWidth(550 - 30)

