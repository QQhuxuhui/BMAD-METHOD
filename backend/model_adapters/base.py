"""
模型适配器基类

定义所有模型适配器必须实现的抽象接口。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncIterator
from pydantic import BaseModel, Field
import structlog


class ModelResponse(BaseModel):
    """模型响应数据模型"""

    content: str = Field(description="模型生成的文本内容")
    tokens_used: int = Field(description="使用的token数量")
    cost: float = Field(description="本次调用的成本（USD）")
    model: str = Field(description="实际使用的模型名称")
    finish_reason: str = Field(description="完成原因：stop/length/error等")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="额外的元数据信息"
    )


class BaseModelAdapter(ABC):
    """所有模型适配器的抽象基类

    所有具体的模型适配器（Qwen/GLM/DeepSeek等）必须继承此类
    并实现所有抽象方法。
    """

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model_name: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        timeout: float = 30.0,
        **kwargs
    ):
        """初始化模型适配器

        Args:
            api_key: API密钥
            base_url: API基础URL
            model_name: 模型名称
            max_tokens: 最大token数
            temperature: 温度参数
            timeout: 请求超时时间（秒）
            **kwargs: 其他自定义参数
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout
        self.extra_params = kwargs
        self.logger = structlog.get_logger(adapter=self.__class__.__name__)

    @abstractmethod
    async def chat(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> ModelResponse:
        """发送聊天消息，返回完整响应

        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            **kwargs: 额外的请求参数（如temperature, max_tokens等）

        Returns:
            ModelResponse: 模型响应对象

        Raises:
            ModelUnavailableError: 模型服务不可用
            ModelTimeoutError: 请求超时
            ModelQuotaExceededError: 配额超限
            ModelResponseError: 响应格式错误
        """
        pass

    @abstractmethod
    async def chat_stream(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> AsyncIterator[str]:
        """流式聊天，逐个yield生成的token

        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            **kwargs: 额外的请求参数

        Yields:
            str: 每个生成的token或文本片段

        Raises:
            ModelUnavailableError: 模型服务不可用
            ModelTimeoutError: 请求超时
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """检查模型服务是否可用

        Returns:
            bool: True表示服务正常，False表示不可用
        """
        pass

    def calculate_cost(self, tokens: int) -> float:
        """根据token数量计算成本

        默认实现返回0，子类可以重写此方法提供具体的计费逻辑。

        Args:
            tokens: 使用的token数量

        Returns:
            float: 成本（USD）
        """
        return 0.0

    def _build_headers(self) -> Dict[str, str]:
        """构建HTTP请求头

        默认实现包含Authorization和Content-Type，
        子类可以重写以添加特定的headers。

        Returns:
            Dict[str, str]: HTTP请求头字典
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _prepare_messages(
        self, messages: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """预处理消息列表

        默认实现直接返回原消息，子类可以重写以进行格式转换。

        Args:
            messages: 原始消息列表

        Returns:
            List[Dict[str, str]]: 处理后的消息列表
        """
        return messages

    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        pass
