# -*- coding:utf-8 -*-


class AppException(Exception):
    """系统异常
    """

    def __init__(self, value=None):
        self._type = type(self)
        self._error_code = error_code_mapper.get(self._type)[0]
        if value:
            self._error_message = value
        else:
            self._error_message = error_code_mapper.get(self._type)[1]
        super().__init__(self._error_message)

    def error_code(self):
        return self._error_code


class AppInvalidRequest(AppException):
    """无效请求
    """

    def __init__(self, value=None):
        super().__init__(value)


class AppAccessDeny(AppException):
    """拒绝访问
    """

    def __init__(self):
        super().__init__()


class AppMissingUser(AppException):
    """没有对应的用户
    """

    def __init__(self):
        super().__init__()


class AppGitHubRequestError(AppException):
    """请求 Github 失败
    """

    def __init__(self):
        super().__init__()


error_code_mapper = {
    AppException: (1000, "系统异常"),
    AppInvalidRequest: (1001, "无效请求"),
    AppAccessDeny: (1002, "拒绝访问"),
    AppMissingUser: (1003, "没有对应的用户"),
    AppGitHubRequestError: (1004, "请求 Github 失败"),
}
