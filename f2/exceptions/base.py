# path: f2/exceptions/base.py


class F2Error(Exception):
    """
    F2 所有自定义异常的根类 (Root of every exception raised by F2)

    作为库使用时只需捕获它即可覆盖接口、配置、数据库与文件四类错误；
    CLI 捕获到它会记录错误并以退出码 1 结束。
    """
