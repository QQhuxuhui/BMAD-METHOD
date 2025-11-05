"""
模型配置数据结构

定义模型适配器的配置参数。
"""

from typing import Literal, Optional, Dict, Any
from pydantic import BaseModel, Field


ModelProvider = Literal["qwen", "glm", "deepseek", "vllm", "ollama"]


class ModelConfig(BaseModel):
    """模型配置数据模型

    用于配置和管理不同模型提供商的参数。
    """

    name: str = Field(description="模型配置名称，全局唯一")
    provider: ModelProvider = Field(description="模型提供商")
    api_key: str = Field(description="API密钥")
    api_base_url: str = Field(description="API基础URL")
    model_version: str = Field(description="模型版本，如qwen-turbo/glm-4/deepseek-chat")
    max_tokens: int = Field(default=4096, ge=1, le=32768, description="最大token数")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="温度参数")
    timeout: float = Field(default=30.0, ge=1.0, le=300.0, description="请求超时时间（秒）")
    is_active: bool = Field(default=True, description="是否启用此配置")
    priority: int = Field(default=0, description="优先级，数值越大优先级越高")
    extra_params: Optional[Dict[str, Any]] = Field(
        default=None, description="额外的自定义参数"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "qwen-turbo-production",
                "provider": "qwen",
                "api_key": "sk-xxx",
                "api_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "model_version": "qwen-turbo",
                "max_tokens": 4096,
                "temperature": 0.7,
                "timeout": 30.0,
                "is_active": True,
                "priority": 1,
                "extra_params": {"top_p": 0.9},
            }
        }


class CostConfig(BaseModel):
    """成本计费配置

    定义不同模型的计费规则。
    """

    input_price_per_1k: float = Field(
        description="输入token价格（每1000 tokens，USD）"
    )
    output_price_per_1k: float = Field(
        description="输出token价格（每1000 tokens，USD）"
    )
    currency: str = Field(default="USD", description="货币单位")

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """计算总成本

        Args:
            input_tokens: 输入token数量
            output_tokens: 输出token数量

        Returns:
            float: 总成本（USD）
        """
        input_cost = (input_tokens / 1000) * self.input_price_per_1k
        output_cost = (output_tokens / 1000) * self.output_price_per_1k
        return input_cost + output_cost


# 预定义各模型的成本配置
DEFAULT_COST_CONFIGS: Dict[str, CostConfig] = {
    # Qwen (通义千问) - 价格参考：https://help.aliyun.com/zh/dashscope/developer-reference/tongyi-thousand-questions-metering-and-billing
    "qwen-turbo": CostConfig(input_price_per_1k=0.0008, output_price_per_1k=0.002),
    "qwen-plus": CostConfig(input_price_per_1k=0.004, output_price_per_1k=0.012),
    "qwen-max": CostConfig(input_price_per_1k=0.04, output_price_per_1k=0.12),
    # GLM (智谱AI) - 价格参考：https://open.bigmodel.cn/pricing
    "glm-4": CostConfig(input_price_per_1k=0.1, output_price_per_1k=0.1),
    "glm-4-flash": CostConfig(input_price_per_1k=0.0001, output_price_per_1k=0.0001),
    # DeepSeek - 价格参考：https://platform.deepseek.com/api-docs/pricing/
    "deepseek-chat": CostConfig(input_price_per_1k=0.0001, output_price_per_1k=0.0002),
    "deepseek-coder": CostConfig(input_price_per_1k=0.0001, output_price_per_1k=0.0002),
    # 本地部署模型成本为0
    "local": CostConfig(input_price_per_1k=0.0, output_price_per_1k=0.0),
}
