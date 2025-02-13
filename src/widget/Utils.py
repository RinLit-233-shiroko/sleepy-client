from loguru import logger

from src.widget.BaseWidget import BaseWidget
from src.widget.mould.DayProgressWidget import DayProgressWidget
from src.widget.mould.PhotoWidget import PhotoWidget
from src.widget.mould.StatusWidget import StatusWidget
from src.widget.mould.WindowDetectionWidget import WindowDetectionWidget

widgets_config = {
    'base': BaseWidget,
    'state': StatusWidget,
    'day_progress': DayProgressWidget,
    'window-detection': WindowDetectionWidget,
    'photo': PhotoWidget
}

widgets_names = {
    'base': '基本组件(测试用)',
    'state': '切换状态',
    'day_progress': '今日进度',
    'window-detection': '窗口检测',
    'photo': '照片墙'
}

def find_key(dictionary, value):
    for key, val in dictionary.items():
        if val == value:
            return key
    logger.warning(f'未找到对应的键值对：{value}')
    return 'base'


def get_widget(widget_name):
    for widget in widgets_config:
        if widget == widget_name:
            return widgets_config[widget]
    return BaseWidget