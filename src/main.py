import sys

from src import config as cf

from PyQt5 import uic
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QGridLayout

from qfluentwidgets import FluentWindow, SplashScreen, setTheme, Theme, LineEdit, FluentIcon as fIcon, \
    TransparentToolButton, PasswordLineEdit, ListWidget, MessageBoxBase, SubtitleLabel, BodyLabel, InfoBar, \
    InfoBarPosition, HyperlinkLabel
from nt_thread import getListThread, getDictThread
from loguru import logger
from random import randint

from src.widget.Utils import widgets_names, find_key, get_widget

# 适配高DPI缩放
QApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

# loguru
logger.add("logs/sleepy_client_win_{{time}}.log", rotation="1 MB", encoding="utf-8",
           retention="3 days")

random_number = randint(1000, 9999)
DEFAULT_CONFIG = {
    "sever": "",
    "secret": "",
    "device_name": f"PC {random_number}",
    "device_id": f"pc-{random_number}",
    "check_interval": 2000,
    "widgets": [
        "state",
        "window-detection"
    ]
}


def update_cf_var(config):
    cf.server = config.get('sever')
    cf.secret = config.get('secret')
    cf.device_name = config.get('device_name')
    cf.device_id = config.get('device_id')
    cf.widgets_config = config.get('widgets')


class AddWidgetDialog(MessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.titleLabel = SubtitleLabel()
        self.captionLabel = BodyLabel()

        self.titleLabel.setText('添加组件')
        self.captionLabel.setText('请选择组件类型')

        self.widget.setMinimumWidth(350)
        self.widget.setMinimumHeight(400)
        self.widgets_list = ListWidget()
        self.widgets_list.addItems(widgets_names.values())
        self.widgets_list.itemSelectionChanged.connect(lambda: self.yesButton.setEnabled(True))

        self.yesButton.setText('添加本组件')
        self.yesButton.clicked.connect(self.add_widget)
        self.yesButton.setEnabled(False)
        self.cancelButton.setText('取消')

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.captionLabel)
        self.viewLayout.addWidget(self.widgets_list)

    def add_widget(self):
        selected_widget = self.widgets_list.selectedItems()
        if not selected_widget:
            return
        widget_name = selected_widget[0].text()
        widget_code = find_key(widgets_names, widget_name)
        if widget_code not in cf.widgets_config:
            cf.widgets_config.append(widget_code)
        else:
            logger.info(f'组件{widget_name}已存在')
            InfoBar.info(
                title='组件已存在',
                content=f'组件“{widget_name}”已存在',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=-1,  # 永不消失
                parent=self.parent()
            )


class SleepyClient(FluentWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 初始化配置
        cf.config = cf.ConfigMgr('.', 'config.json')
        cf.config.load_config(DEFAULT_CONFIG)
        update_cf_var(cf.config)

        # 加载 UI
        self.dashboard_interface = uic.loadUi('./assets/ui/main.ui')
        self.dashboard_interface.setObjectName('mainPage')
        self.settings_interface = uic.loadUi('./assets/ui/settings.ui')
        self.dashboard_interface.setObjectName('settingsPage')

        self.widgets_grid = None
        self.add_widget = None
        self.get_json_thread = None
        self.get_status_list_thread = None
        self.callback_counter = 0

        self.initUi()
        self.init_subInterface()

        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.get_all_json()

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(lambda: update_cf_var(cf.config))
        self.update_timer.start(1000)

    def setup_settings(self):
        """
        设置界面
        """

        sever_input = self.settings_interface.findChild(LineEdit, 'server')
        sever_input.setText(cf.server)
        sever_input.textChanged.connect(lambda text: cf.config.upload_config('sever', text))

        secret_input = self.settings_interface.findChild(PasswordLineEdit, 'secret')
        secret_input.setText(cf.secret)
        secret_input.textChanged.connect(lambda text: cf.config.upload_config('secret', text))

        device_id_input = self.settings_interface.findChild(LineEdit, 'device_id')
        device_id_input.setText(cf.device_id)
        device_id_input.textChanged.connect(lambda text: cf.config.upload_config('device_id', text))

        github_link = self.settings_interface.findChild(HyperlinkLabel, 'github_link')
        github_link.setUrl(QUrl('https://github.com/RinLit-233-shiroko/sleepy-client'))
        bilibili_link = self.settings_interface.findChild(HyperlinkLabel, 'bilibili_link')
        bilibili_link.setUrl(QUrl('https://space.bilibili.com/569522843'))

    def setup_dashboard(self):
        """
        仪表板界面
        """
        self.add_widget = self.dashboard_interface.findChild(TransparentToolButton, 'add_widget')
        self.add_widget.setIcon(fIcon.ADD)
        self.add_widget.clicked.connect(self.add_widget_dialog)

        self.widgets_grid = self.dashboard_interface.findChild(QGridLayout, 'widgets_grid')
        self.widgets_grid.setSpacing(12)
        self.add_widgets()

    def setup_failed_dashboard(self, error_msg):
        max_letter = 200
        if len(error_msg) > max_letter:
            error_msg = error_msg[:max_letter] + '...'

        self.splashScreen.finish()
        InfoBar.warning(
            title='无法加载（；´д｀）ゞ',
            content=error_msg,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM,
            duration=-1,  # 永不消失
            parent=self
        )

    def add_widget_dialog(self):
        aw_dialog = AddWidgetDialog(self)
        if aw_dialog.exec():
            self.add_widgets()

    def add_widgets(self):
        cf.config.save_config()
        # remove original
        while self.widgets_grid.count():
            item = self.widgets_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # re-add
        for i in range(len(cf.widgets_config)):
            # 行列
            row = i // 2
            col = i % 2

            widget_class = get_widget(cf.widgets_config[i])  # 获取 BaseWidget 类
            w = widget_class(
                parent=self, layout=self.widgets_grid
            )
            self.widgets_grid.addWidget(w, row, col)

    def get_all_json(self):
        def check_callbacks():
            if self.callback_counter == -1:
                logger.error('数据获取失败，请检查网络连接')

            self.callback_counter += 1
            if self.callback_counter == 2:
                logger.success('所有数据获取成功')
                self.splashScreen.finish()
                self.setup_dashboard()

        def callback_status(data):
            if 'error' in data:
                logger.error(f'获取状态列表失败：{data["error"]}')
                self.callback_counter = -1
                self.setup_failed_dashboard(f'获取状态列表失败：{data["error"]}')
                return
            cf.status_info = data['info']
            logger.debug(f'当前状态：{cf.status_info}')
            check_callbacks()

        def callback_list(data):
            if len(data) == 1:
                logger.error(f'获取状态列表失败：{data}')
                self.callback_counter = -1
                self.setup_failed_dashboard(f'获取状态列表失败：{data}')
                return
            for status in data:
                cf.status_dict[status['id']] = f"{status['name']} - {status['desc']}"
            logger.debug(f'所有状态列表：{cf.status_dict}')
            check_callbacks()

        if cf.server == '':  # 未设置服务器地址
            logger.error('请先设置服务器地址')
            self.setup_failed_dashboard("请先在“设置”页中设置您的服务器地址")
            return

        self.get_json_thread = getDictThread(f'{cf.server}/query')
        self.get_json_thread.json_signal.connect(callback_status)
        self.get_json_thread.start()

        self.get_status_list_thread = getListThread(f'{cf.server}/status_list')
        self.get_status_list_thread.json_signal.connect(callback_list)
        self.get_status_list_thread.start()
        logger.debug('正在获取所有数据')

    def init_subInterface(self):
        self.addSubInterface(self.dashboard_interface, fIcon.TILES, '仪表板')
        self.addSubInterface(self.settings_interface, fIcon.SETTING, '设置', )

        self.setup_settings()

    def initUi(self):
        setTheme(Theme.AUTO)
        screen_size = app.primaryScreen().size()
        self.resize(900, 600)
        self.move((screen_size.width() - self.width()) // 2, (screen_size.height() - self.height()) // 2)
        self.setMinimumSize(400, 300)
        self.setWindowTitle('Sleepy Client')
        self.setWindowIcon(QIcon('../assets/images/favicon.png'))
        self.navigationInterface.setExpandWidth(150)
        self.navigationInterface.setMinimumExpandWidth(200)
        self.navigationInterface.expand(useAni=False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SleepyClient()
    window.show()
    logger.info('Sleepy Client，启动！')
    app.exec_()
