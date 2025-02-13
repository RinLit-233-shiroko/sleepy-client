from state_console import loadjson
from PyQt5.QtCore import QThread, pyqtSignal

from window_detection import do_update, post_to_api


class getDictThread(QThread):
    json_signal = pyqtSignal(dict)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        data = self.get_data()
        if type(data) is str:
            data = {'error': data}
        self.json_signal.emit(data)

    def get_data(self):
        data = loadjson(f'{self.url}')
        return data


class getListThread(QThread):
    json_signal = pyqtSignal(list)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        data = self.get_data()
        if type(data) is str:
            data = [data]
        self.json_signal.emit(data)

    def get_data(self):
        data = loadjson(f'{self.url}')
        return data


class postThread(QThread):
    list_signal = pyqtSignal(list)

    def __init__(self, fake_name):
        super().__init__()
        self.window = None
        self.fake_window = fake_name
        self.using = None

    def run(self):
        self.window, self.using = do_update()
        data = self.post_data()
        self.list_signal.emit([self.window, data])  # 返回两个参（窗口名+网络返回值）

    def post_data(self):
        if self.fake_window != '':
            self.window = self.fake_window
        response = post_to_api(self.window, self.using)
        return response
