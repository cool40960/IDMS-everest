"""自定义异常（设计稿 §八）。

各驱动只抛这里的异常，main.py 的异常处理器按 http_status 统一翻成
{"error": "..."}，前台不接触底层 K8s/Everest 报错。

参数格式错误用 Pydantic 自带的 ValidationError（→400），不在这里自定义。
"""


class IDMSError(Exception):
    """所有 IDMS 业务异常的基类。"""

    http_status = 500

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class AlreadyExistsError(IDMSError):
    """实例重名（底层 409 归一到这里）。"""

    http_status = 409


class NotFoundError(IDMSError):
    """实例不存在（底层 404 归一到这里）。"""

    http_status = 404


class UpstreamError(IDMSError):
    """K8s / Operator / Everest 上游故障。"""

    http_status = 502
