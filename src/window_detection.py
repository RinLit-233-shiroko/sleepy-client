# coding: utf-8
'''
win_device.py
在 Windows 上获取窗口名称
by: @wyf9
依赖: pywin32, requests
'''
from win32gui import GetWindowText, GetForegroundWindow  # type: ignore
from requests import post
from datetime import datetime
from src import config as cf

# --- config start
BYPASS_SAME_REQUEST = True
ENCODING = 'utf-8'  # 控制台输出所用编码，避免编码出错，可选 utf-8 或 gb18030
SKIPPED_NAMES = ['', '系统托盘溢出窗口。', '新通知', '任务切换']  # 当窗口名为其中任意一项时将不更新
NOT_USING_NAMES = ['我们喜欢这张图片，因此我们将它与你共享。']  # 当窗口名为其中任意一项时视为未在使用
# --- config end

# stdout = TextIOWrapper(stdout.buffer, encoding=ENCODING)  # https://stackoverflow.com/a/3218048/28091753
_print_ = print


def print(msg: str, **kwargs):
    '''
    修改后的 `print()` 函数，解决不刷新日志的问题
    原: `_print_()`
    '''
    _print_(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {msg}', flush=True, **kwargs)


last_window = ''


def do_update():
    global last_window
    window = GetWindowText(GetForegroundWindow())  # type: ignore
    print(f'--- Window: `{window}`')

    # 判断是否在使用
    using = True
    for i in NOT_USING_NAMES:
        if i == window:
            print(f'* not using: `{i}`')
            using = False

    # 检测重复名称
    if BYPASS_SAME_REQUEST and window == last_window:
        print('window not change, bypass')
        return last_window, using

    # 检查跳过名称
    for i in SKIPPED_NAMES:
        if i == window:
            print(f'* skipped: `{i}`')
            return last_window, using

    # response = post_to_api(window, using)

    last_window = window
    return window, using


def post_to_api(window, using):
    # POST to api
    print(f'POST {cf.server}')
    try:
        resp = post(url=f'{cf.server}/device/set', json={
            'secret': cf.secret,
            'id': cf.device_id,
            'show_name': cf.device_name,
            'using': using,
            'app_name': window
        }, headers={
            'Content-Type': 'application/json'
        }, proxies={
            'https': None,
            'http': None
        })
        print(f'Response: {resp.status_code} - {resp.json()}')
        return resp.json()
    except Exception as e:
        print(f'Error: {e}')
        return f'Error: {e}'


# def main():
#     while True:
#         do_update()
#         sleep(CHECK_INTERVAL)


# if __name__ == '__main__':
#     try:
#         main()
#     except KeyboardInterrupt as e:
#         # 如果中断则发送未在使用
#         print(f'Interrupt: {e}')
#         try:
#             resp = post(url=Url, json={
#                 'secret': SECRET,
#                 'id': DEVICE_ID,
#                 'show_name': DEVICE_SHOW_NAME,
#                 'using': False,
#                 'app_name': f'{e}'
#             }, headers={
#                 'Content-Type': 'application/json',
#             }, proxies={
#                 'https': None,
#                 'http': None
#             })
#             print(f'Response: {resp.status_code} - {resp.json()}')
#         except Exception as e:
#             print(f'Error: {e}')
