"""
模型适配器自定义异常

定义所有模型适配器可能抛出的异常类型。
"""


class ModelAdapterError(Exception):
    """模型适配器基础异常"""

    pass


class ModelUnavailableError(ModelAdapterError):
    """模型服务不可用异常

    当模型API端点无法访问或健康检查失败时抛出。
    """

    pass


class ModelTimeoutError(ModelAdapterError):
    """模型请求超时异常

    当模型API请求超过设定的超时时间时抛出。
    """

    pass


class ModelQuotaExceededError(ModelAdapterError):
    """配额超限异常

    当API调用超过配额限制时抛出。
    """

    pass


class ModelConfigurationError(ModelAdapterError):
    """模型配置错误异常

    当模型配置参数无效或缺失时抛出。
    """

    pass


class ModelResponseError(ModelAdapterError):
    """模型响应错误异常

    当模型返回的响应格式不符合预期时抛出。
    """

    pass
