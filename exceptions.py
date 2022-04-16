class ApiError(Exception):
    """
    调用API时出现错误
    """
    pass


class LoginError(ApiError):
    """
    当你的登录状态失效时会抛出这个错误
    """
    pass


class AlreadyChosen(ApiError):
    """
    已报名过该课程，请不要重复报名
    """


class FailedToChoose(ApiError):
    """
    选课失败，该课程不可选择
    """


class FailedToDelChosen(ApiError):
    """
    退选失败，未找到退选课程或已超过退选时间
    """
