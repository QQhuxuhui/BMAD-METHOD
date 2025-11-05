"""
模型配置数据模型

存储模型适配器的配置信息。
"""

from datetime import datetime, UTC
from typing import Literal, Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel
from pydantic import field_validator

from app.models.base import BaseModel


# 允许的模型提供商
ALLOWED_PROVIDERS = ["qwen", "glm", "deepseek", "vllm", "ollama"]


class ModelConfigBase(SQLModel):
    """模型配置基础字段"""

    name: str = Field(
        unique=True,
        index=True,
        description="模型配置的唯一名称",
        max_length=100,
    )
    provider: str = Field(
        description="模型提供商",
        index=True,
        max_length=50,
    )

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """验证provider字段值"""
        if v not in ALLOWED_PROVIDERS:
            raise ValueError(
                f"Provider must be one of {ALLOWED_PROVIDERS}, got: {v}"
            )
        return v
    api_base_url: str = Field(
        description="API基础URL",
        max_length=500,
    )
    model_version: str = Field(
        description="模型版本/名称",
        max_length=100,
    )
    max_tokens: int = Field(
        default=4096,
        ge=1,
        le=128000,
        description="最大生成token数",
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="采样温度",
    )
    is_active: bool = Field(
        default=True,
        index=True,
        description="是否启用此配置",
    )
    priority: int = Field(
        default=0,
        description="优先级（数值越大优先级越高）",
    )
    description: Optional[str] = Field(
        default=None,
        description="配置描述",
        max_length=500,
    )


class ModelConfig(BaseModel, ModelConfigBase, table=True):
    """模型配置数据模型（数据库表）

    存储模型适配器的配置信息，包括API密钥等敏感信息。
    """

    __tablename__ = "model_configs"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="配置ID",
    )

    api_key_encrypted: Optional[str] = Field(
        default=None,
        description="加密后的API密钥",
        max_length=500,
    )

    timeout: float = Field(
        default=30.0,
        ge=1.0,
        le=600.0,
        description="请求超时时间（秒）",
    )

    # 额外配置（JSON格式存储）
    extra_params: Optional[str] = Field(
        default=None,
        description="额外参数（JSON字符串）",
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="最后更新时间",
    )

    # 使用统计
    total_requests: int = Field(
        default=0,
        ge=0,
        description="总请求次数",
    )

    total_tokens: int = Field(
        default=0,
        ge=0,
        description="总消耗token数",
    )

    total_cost: float = Field(
        default=0.0,
        ge=0.0,
        description="总成本（USD）",
    )

    last_used_at: Optional[datetime] = Field(
        default=None,
        description="最后使用时间",
    )


class ModelConfigCreate(ModelConfigBase):
    """创建模型配置的请求模型"""

    api_key: str = Field(
        description="API密钥（明文，将被加密存储）",
        min_length=1,
        max_length=500,
    )
    timeout: float = Field(
        default=30.0,
        ge=1.0,
        le=600.0,
        description="请求超时时间（秒）",
    )
    extra_params: Optional[str] = Field(
        default=None,
        description="额外参数（JSON字符串）",
    )


class ModelConfigUpdate(SQLModel):
    """更新模型配置的请求模型"""

    name: Optional[str] = Field(
        default=None,
        max_length=100,
    )
    provider: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: Optional[str]) -> Optional[str]:
        """验证provider字段值"""
        if v is not None and v not in ALLOWED_PROVIDERS:
            raise ValueError(
                f"Provider must be one of {ALLOWED_PROVIDERS}, got: {v}"
            )
        return v
    api_base_url: Optional[str] = Field(
        default=None,
        max_length=500,
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API密钥（明文，将被加密存储）",
        max_length=500,
    )
    model_version: Optional[str] = Field(
        default=None,
        max_length=100,
    )
    max_tokens: Optional[int] = Field(
        default=None,
        ge=1,
        le=128000,
    )
    temperature: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=2.0,
    )
    timeout: Optional[float] = Field(
        default=None,
        ge=1.0,
        le=600.0,
    )
    is_active: Optional[bool] = None
    priority: Optional[int] = None
    description: Optional[str] = Field(
        default=None,
        max_length=500,
    )
    extra_params: Optional[str] = None


class ModelConfigRead(ModelConfigBase):
    """读取模型配置的响应模型（不包含敏感信息）"""

    id: UUID
    timeout: float
    total_requests: int
    total_tokens: int
    total_cost: float
    last_used_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    # 不返回api_key_encrypted和extra_params以保护敏感信息


class ModelConfigReadWithKey(ModelConfigRead):
    """读取模型配置的响应模型（包含API密钥）

    仅用于需要显示API密钥的特殊场景（如管理员操作）。
    """

    api_key_encrypted: Optional[str] = None
