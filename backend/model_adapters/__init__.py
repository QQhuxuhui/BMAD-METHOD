"""
国产模型适配器模块

提供统一的模型调用接口，支持多种国产大模型和本地推理引擎。
"""

from model_adapters.base import BaseModelAdapter, ModelResponse
from model_adapters.exceptions import (
    ModelAdapterError,
    ModelUnavailableError,
    ModelTimeoutError,
    ModelQuotaExceededError,
)

__all__ = [
    "BaseModelAdapter",
    "ModelResponse",
    "ModelAdapterError",
    "ModelUnavailableError",
    "ModelTimeoutError",
    "ModelQuotaExceededError",
]
