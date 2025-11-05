"""
模型适配器指标记录工具

提供便捷的方法来记录Prometheus指标。
"""

import time
from typing import Optional, Dict, Any
from contextlib import contextmanager
import structlog

from app.core.metrics import (
    model_requests_total,
    model_request_duration_seconds,
    model_errors_total,
    model_tokens_used_total,
    model_cost_total,
    active_models_count,
    model_health_status,
    model_health_check_duration_seconds,
)

logger = structlog.get_logger(__name__)


class ModelMetricsRecorder:
    """模型指标记录器

    用于记录模型适配器的各项指标。
    """

    def __init__(self, model_name: str, provider: str):
        """初始化指标记录器

        Args:
            model_name: 模型名称
            provider: 提供商名称
        """
        self.model_name = model_name
        self.provider = provider

    @contextmanager
    def record_request(self):
        """记录模型请求的上下文管理器

        自动记录请求的成功/失败、延迟等信息。

        Usage:
            with recorder.record_request():
                response = await model.chat(messages)
        """
        start_time = time.time()
        error_occurred = False
        error_type = None

        try:
            yield
            # 请求成功
            model_requests_total.labels(
                model_name=self.model_name,
                provider=self.provider,
                status="success",
            ).inc()

        except Exception as e:
            # 请求失败
            error_occurred = True
            error_type = type(e).__name__

            model_requests_total.labels(
                model_name=self.model_name,
                provider=self.provider,
                status="error",
            ).inc()

            model_errors_total.labels(
                model_name=self.model_name,
                provider=self.provider,
                error_type=error_type,
            ).inc()

            logger.error(
                "model_request_error",
                model=self.model_name,
                provider=self.provider,
                error=str(e),
            )
            raise

        finally:
            # 记录延迟
            duration = time.time() - start_time
            model_request_duration_seconds.labels(
                model_name=self.model_name,
                provider=self.provider,
            ).observe(duration)

    def record_tokens(
        self, input_tokens: int, output_tokens: int
    ):
        """记录token使用量

        Args:
            input_tokens: 输入token数量
            output_tokens: 输出token数量
        """
        model_tokens_used_total.labels(
            model_name=self.model_name,
            provider=self.provider,
            token_type="input",
        ).inc(input_tokens)

        model_tokens_used_total.labels(
            model_name=self.model_name,
            provider=self.provider,
            token_type="output",
        ).inc(output_tokens)

    def record_cost(self, cost: float):
        """记录API调用成本

        Args:
            cost: 成本（USD）
        """
        model_cost_total.labels(
            model_name=self.model_name,
            provider=self.provider,
        ).inc(cost)

    def record_health_status(self, is_healthy: bool):
        """记录健康状态

        Args:
            is_healthy: 是否健康
        """
        status_value = 1 if is_healthy else 0
        model_health_status.labels(
            model_name=self.model_name,
            provider=self.provider,
        ).set(status_value)

    @contextmanager
    def record_health_check(self):
        """记录健康检查的上下文管理器

        自动记录健康检查的延迟。

        Usage:
            with recorder.record_health_check():
                is_healthy = await model.health_check()
        """
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            model_health_check_duration_seconds.labels(
                model_name=self.model_name,
                provider=self.provider,
            ).observe(duration)


def update_active_models_count(provider_counts: Dict[str, int]):
    """更新活跃模型数量

    Args:
        provider_counts: 提供商到模型数量的映射
    """
    for provider, count in provider_counts.items():
        active_models_count.labels(provider=provider).set(count)


def record_model_response(
    model_name: str,
    provider: str,
    response: Any,
):
    """便捷方法：记录模型响应的完整指标

    Args:
        model_name: 模型名称
        provider: 提供商
        response: ModelResponse对象
    """
    recorder = ModelMetricsRecorder(model_name, provider)

    # 记录token使用（如果响应包含metadata）
    if hasattr(response, "metadata") and response.metadata:
        input_tokens = response.metadata.get("input_tokens", 0)
        output_tokens = response.metadata.get("output_tokens", 0)
        if input_tokens or output_tokens:
            recorder.record_tokens(input_tokens, output_tokens)

    # 记录成本
    if hasattr(response, "cost") and response.cost:
        recorder.record_cost(response.cost)

    logger.info(
        "model_response_recorded",
        model=model_name,
        provider=provider,
        tokens=response.tokens_used if hasattr(response, "tokens_used") else 0,
        cost=response.cost if hasattr(response, "cost") else 0,
    )
