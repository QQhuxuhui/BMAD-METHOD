"""
DeepSeek模型适配器

支持DeepSeek官方API和私有化部署版本（如DeepSeek-R1）。
DeepSeek API兼容OpenAI格式，实现简洁高效。

API文档: https://platform.deepseek.com/api-docs/
"""

from typing import List, Dict, Any, AsyncIterator, Optional
import httpx
import structlog

from model_adapters.base import BaseModelAdapter, ModelResponse
from model_adapters.config import CostConfig, DEFAULT_COST_CONFIGS
from model_adapters.retry_utils import call_model_api
from model_adapters.exceptions import ModelResponseError

logger = structlog.get_logger(__name__)


class DeepSeekAdapter(BaseModelAdapter):
    """DeepSeek模型适配器

    支持DeepSeek-V2、DeepSeek-V3、DeepSeek-Coder等模型。
    也支持私有化部署的DeepSeek-R1等模型。

    API格式遵循OpenAI标准，易于集成。
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.deepseek.com/v1",
        model_name: str = "deepseek-chat",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        timeout: float = 30.0,
        **kwargs
    ):
        """初始化DeepSeek适配器

        Args:
            api_key: DeepSeek API密钥
            base_url: API基础URL，默认为官方API，可配置为私有部署地址
            model_name: 模型名称（如deepseek-chat/deepseek-coder/service-deepseek-r1-0528）
            max_tokens: 最大生成token数
            temperature: 采样温度
            timeout: 请求超时时间（秒）
            **kwargs: 额外参数（如top_p, frequency_penalty等）
        """
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            model_name=model_name,
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=timeout,
            **kwargs
        )
        self.cost_config = self._get_cost_config(model_name)

    def _get_cost_config(self, model_name: str) -> Optional[CostConfig]:
        """获取模型的计费配置

        Args:
            model_name: 模型名称

        Returns:
            CostConfig: 计费配置，如果模型未在预定义配置中则返回None
        """
        # 尝试精确匹配
        if model_name in DEFAULT_COST_CONFIGS:
            return DEFAULT_COST_CONFIGS[model_name]

        # 尝试前缀匹配（用于识别不同版本的模型）
        for key in DEFAULT_COST_CONFIGS:
            if model_name.startswith(key):
                return DEFAULT_COST_CONFIGS[key]

        # 私有化部署或未知模型使用默认本地配置（成本为0）
        logger.warning(
            "unknown_model_cost",
            model=model_name,
            message="使用默认本地计费配置（成本为0）",
        )
        return DEFAULT_COST_CONFIGS.get("local")

    async def chat(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> ModelResponse:
        """发送聊天请求到DeepSeek API

        Args:
            messages: 消息列表，格式 [{"role": "user/assistant/system", "content": "..."}]
            **kwargs: 额外参数，如temperature, max_tokens等

        Returns:
            ModelResponse: 模型响应对象

        Raises:
            ModelUnavailableError: 服务不可用
            ModelTimeoutError: 请求超时
            ModelResponseError: 响应格式错误
        """
        # 准备请求参数
        url = f"{self.base_url}/chat/completions"
        headers = self._build_headers()

        # 合并参数（kwargs优先级更高）
        request_params = {
            "model": self.model_name,
            "messages": self._prepare_messages(messages),
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            **self.extra_params,
            **kwargs,
        }

        logger.info(
            "deepseek_chat_request",
            model=self.model_name,
            num_messages=len(messages),
        )

        # 调用API
        response = await call_model_api(
            url=url,
            headers=headers,
            data=request_params,
            timeout=self.timeout,
        )

        # 解析响应
        return self._parse_response(response.json())

    async def chat_stream(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> AsyncIterator[str]:
        """流式聊天请求

        Args:
            messages: 消息列表
            **kwargs: 额外参数

        Yields:
            str: 每个生成的token片段
        """
        url = f"{self.base_url}/chat/completions"
        headers = self._build_headers()

        request_params = {
            "model": self.model_name,
            "messages": self._prepare_messages(messages),
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": True,  # 启用流式输出
            **self.extra_params,
            **kwargs,
        }

        logger.info(
            "deepseek_stream_request",
            model=self.model_name,
            num_messages=len(messages),
        )

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                url,
                headers=headers,
                json=request_params,
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line or line.startswith(":"):
                        continue

                    if line.startswith("data: "):
                        data = line[6:]  # 移除 "data: " 前缀

                        if data == "[DONE]":
                            break

                        try:
                            import json

                            chunk = json.loads(data)
                            delta = chunk.get("choices", [{}])[0].get(
                                "delta", {}
                            )
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError as e:
                            logger.warning(
                                "stream_parse_error", line=line, error=str(e)
                            )
                            continue

    async def health_check(self) -> bool:
        """健康检查：发送简单请求验证服务可用性

        Returns:
            bool: True表示服务正常，False表示异常
        """
        try:
            test_message = [{"role": "user", "content": "Hi"}]
            response = await self.chat(test_message)
            return bool(response.content)
        except Exception as e:
            logger.error("deepseek_health_check_failed", error=str(e))
            return False

    def calculate_cost(self, tokens: int) -> float:
        """计算API调用成本

        Args:
            tokens: token数量

        Returns:
            float: 成本（USD）
        """
        if not self.cost_config:
            return 0.0

        # DeepSeek的计费通常是input和output相同价格
        # 这里简化处理，实际应该区分input/output tokens
        return (tokens / 1000) * self.cost_config.input_price_per_1k

    def _parse_response(self, response_data: Dict[str, Any]) -> ModelResponse:
        """解析API响应数据

        Args:
            response_data: API返回的JSON数据

        Returns:
            ModelResponse: 标准化的响应对象

        Raises:
            ModelResponseError: 响应格式错误
        """
        try:
            choices = response_data.get("choices", [])
            if not choices:
                raise ModelResponseError("Response missing 'choices' field")

            message = choices[0].get("message", {})
            content = message.get("content", "")
            finish_reason = choices[0].get("finish_reason", "unknown")

            usage = response_data.get("usage", {})
            total_tokens = usage.get("total_tokens", 0)
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)

            # 计算成本
            if self.cost_config:
                cost = self.cost_config.calculate_cost(
                    input_tokens, output_tokens
                )
            else:
                cost = 0.0

            return ModelResponse(
                content=content,
                tokens_used=total_tokens,
                cost=cost,
                model=response_data.get("model", self.model_name),
                finish_reason=finish_reason,
                metadata={
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "usage": usage,
                },
            )

        except KeyError as e:
            logger.error(
                "response_parse_error",
                error=str(e),
                response=response_data,
            )
            raise ModelResponseError(
                f"Failed to parse response: missing field {str(e)}"
            )
