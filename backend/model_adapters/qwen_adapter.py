"""
Qwen（千问）模型适配器

支持阿里云通义千问私有化部署版本。
API兼容OpenAI格式。

私有化部署配置：
- 地址：http://10.90.15.22:8103/v1
- 模型：qwen3-30b-a3b
"""

from typing import List, Dict, Any, AsyncIterator, Optional
import httpx
import structlog

from model_adapters.base import BaseModelAdapter, ModelResponse
from model_adapters.config import CostConfig, DEFAULT_COST_CONFIGS
from model_adapters.retry_utils import call_model_api
from model_adapters.exceptions import ModelResponseError

logger = structlog.get_logger(__name__)


class QwenAdapter(BaseModelAdapter):
    """Qwen（千问）模型适配器

    支持阿里云通义千问官方API和私有化部署版本。
    API格式遵循OpenAI标准。
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1",
        model_name: str = "qwen-turbo",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        timeout: float = 30.0,
        **kwargs
    ):
        """初始化Qwen适配器

        Args:
            api_key: API密钥（私有化部署可以是任意值）
            base_url: API基础URL
            model_name: 模型名称（如qwen-turbo/qwen-plus/qwen3-30b-a3b）
            max_tokens: 最大生成token数
            temperature: 采样温度
            timeout: 请求超时时间（秒）
            **kwargs: 额外参数（如top_p等）
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
            CostConfig: 计费配置
        """
        # 尝试精确匹配
        if model_name in DEFAULT_COST_CONFIGS:
            return DEFAULT_COST_CONFIGS[model_name]

        # 尝试前缀匹配
        for key in DEFAULT_COST_CONFIGS:
            if model_name.startswith(key):
                return DEFAULT_COST_CONFIGS[key]

        # 私有化部署使用本地配置（成本为0）
        logger.info(
            "using_local_cost_config",
            model=model_name,
            message="私有化部署模型，使用本地计费配置（成本为0）",
        )
        return DEFAULT_COST_CONFIGS.get("local")

    async def chat(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> ModelResponse:
        """发送聊天请求到Qwen API

        Args:
            messages: 消息列表，格式 [{"role": "user/assistant/system", "content": "..."}]
            **kwargs: 额外参数

        Returns:
            ModelResponse: 模型响应对象
        """
        url = f"{self.base_url}/chat/completions"
        headers = self._build_headers()

        request_params = {
            "model": self.model_name,
            "messages": self._prepare_messages(messages),
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            **self.extra_params,
            **kwargs,
        }

        logger.info(
            "qwen_chat_request",
            model=self.model_name,
            num_messages=len(messages),
        )

        response = await call_model_api(
            url=url,
            headers=headers,
            data=request_params,
            timeout=self.timeout,
        )

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
            "stream": True,
            **self.extra_params,
            **kwargs,
        }

        logger.info(
            "qwen_stream_request",
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
                        data = line[6:]

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
        """健康检查

        Returns:
            bool: True表示服务正常
        """
        try:
            test_message = [{"role": "user", "content": "Hi"}]
            response = await self.chat(test_message)
            return bool(response.content)
        except Exception as e:
            logger.error("qwen_health_check_failed", error=str(e))
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

        return (tokens / 1000) * self.cost_config.input_price_per_1k

    def _parse_response(self, response_data: Dict[str, Any]) -> ModelResponse:
        """解析API响应数据

        Args:
            response_data: API返回的JSON数据

        Returns:
            ModelResponse: 标准化的响应对象
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
