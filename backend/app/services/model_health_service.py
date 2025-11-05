"""
模型健康检查服务

提供定期健康检查、响应时间监控、成功率统计等功能。
支持自动健康检查和手动触发。
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque
import structlog

from model_adapters.model_factory import ModelFactory
from model_adapters.base import BaseModelAdapter

logger = structlog.get_logger(__name__)


class HealthCheckResult:
    """单次健康检查结果"""

    def __init__(
        self,
        model_name: str,
        is_healthy: bool,
        response_time: float,
        timestamp: datetime,
        error: Optional[str] = None,
    ):
        self.model_name = model_name
        self.is_healthy = is_healthy
        self.response_time = response_time  # 秒
        self.timestamp = timestamp
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "model_name": self.model_name,
            "is_healthy": self.is_healthy,
            "response_time": self.response_time,
            "timestamp": self.timestamp.isoformat(),
            "error": self.error,
        }


class ModelHealthStats:
    """模型健康统计信息"""

    def __init__(self, model_name: str, max_history: int = 100):
        self.model_name = model_name
        self.max_history = max_history
        self.history: deque[HealthCheckResult] = deque(maxlen=max_history)
        self.total_checks = 0
        self.successful_checks = 0
        self.failed_checks = 0
        self.total_response_time = 0.0
        self.last_check_time: Optional[datetime] = None
        self.last_healthy_time: Optional[datetime] = None
        self.consecutive_failures = 0

    def add_check_result(self, result: HealthCheckResult):
        """添加检查结果"""
        self.history.append(result)
        self.total_checks += 1
        self.last_check_time = result.timestamp

        if result.is_healthy:
            self.successful_checks += 1
            self.last_healthy_time = result.timestamp
            self.consecutive_failures = 0
        else:
            self.failed_checks += 1
            self.consecutive_failures += 1

        self.total_response_time += result.response_time

    def get_success_rate(self, window_minutes: int = 60) -> float:
        """获取指定时间窗口内的成功率

        Args:
            window_minutes: 时间窗口（分钟）

        Returns:
            成功率（0.0-1.0）
        """
        if not self.history:
            return 0.0

        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        recent_checks = [
            r for r in self.history if r.timestamp >= cutoff_time
        ]

        if not recent_checks:
            return 0.0

        successful = sum(1 for r in recent_checks if r.is_healthy)
        return successful / len(recent_checks)

    def get_average_response_time(self, window_minutes: int = 60) -> float:
        """获取指定时间窗口内的平均响应时间

        Args:
            window_minutes: 时间窗口（分钟）

        Returns:
            平均响应时间（秒）
        """
        if not self.history:
            return 0.0

        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        recent_checks = [
            r for r in self.history if r.timestamp >= cutoff_time
        ]

        if not recent_checks:
            return 0.0

        total_time = sum(r.response_time for r in recent_checks)
        return total_time / len(recent_checks)

    def get_overall_stats(self) -> Dict[str, Any]:
        """获取总体统计信息"""
        avg_response_time = (
            self.total_response_time / self.total_checks
            if self.total_checks > 0
            else 0.0
        )

        return {
            "model_name": self.model_name,
            "total_checks": self.total_checks,
            "successful_checks": self.successful_checks,
            "failed_checks": self.failed_checks,
            "success_rate": (
                self.successful_checks / self.total_checks
                if self.total_checks > 0
                else 0.0
            ),
            "average_response_time": avg_response_time,
            "last_check_time": (
                self.last_check_time.isoformat()
                if self.last_check_time
                else None
            ),
            "last_healthy_time": (
                self.last_healthy_time.isoformat()
                if self.last_healthy_time
                else None
            ),
            "consecutive_failures": self.consecutive_failures,
            "is_currently_healthy": (
                self.history[-1].is_healthy if self.history else False
            ),
        }


class ModelHealthService:
    """模型健康检查服务

    提供定期健康检查、统计和监控功能。
    """

    def __init__(
        self,
        factory: ModelFactory,
        check_interval: int = 60,
        max_history: int = 100,
        failure_threshold: int = 3,
    ):
        """初始化健康检查服务

        Args:
            factory: 模型工厂实例
            check_interval: 检查间隔（秒）
            max_history: 保留的历史记录数量
            failure_threshold: 连续失败阈值（达到后触发告警）
        """
        self.factory = factory
        self.check_interval = check_interval
        self.max_history = max_history
        self.failure_threshold = failure_threshold

        self.stats: Dict[str, ModelHealthStats] = {}
        self._check_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        """启动定期健康检查"""
        if self._running:
            logger.warning("health_service_already_running")
            return

        self._running = True
        self._check_task = asyncio.create_task(self._periodic_check())
        logger.info(
            "health_service_started",
            check_interval=self.check_interval,
        )

    async def stop(self):
        """停止定期健康检查"""
        if not self._running:
            return

        self._running = False
        if self._check_task:
            self._check_task.cancel()
            try:
                await self._check_task
            except asyncio.CancelledError:
                pass

        logger.info("health_service_stopped")

    async def _periodic_check(self):
        """定期执行健康检查"""
        while self._running:
            try:
                await self.check_all_models()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(
                    "periodic_check_error",
                    error=str(e),
                )
                await asyncio.sleep(self.check_interval)

    async def check_model(self, model_name: str) -> HealthCheckResult:
        """检查单个模型的健康状态

        Args:
            model_name: 模型名称

        Returns:
            HealthCheckResult: 检查结果
        """
        start_time = time.time()
        timestamp = datetime.now()
        error = None

        try:
            adapter = self.factory.get_model(model_name)
            is_healthy = await adapter.health_check()
            response_time = time.time() - start_time

            logger.info(
                "model_health_checked",
                model=model_name,
                is_healthy=is_healthy,
                response_time=response_time,
            )

        except Exception as e:
            is_healthy = False
            response_time = time.time() - start_time
            error = str(e)

            logger.error(
                "model_health_check_failed",
                model=model_name,
                error=error,
                response_time=response_time,
            )

        result = HealthCheckResult(
            model_name=model_name,
            is_healthy=is_healthy,
            response_time=response_time,
            timestamp=timestamp,
            error=error,
        )

        # 更新统计信息
        if model_name not in self.stats:
            self.stats[model_name] = ModelHealthStats(
                model_name, self.max_history
            )

        self.stats[model_name].add_check_result(result)

        # 检查是否需要告警
        if (
            self.stats[model_name].consecutive_failures
            >= self.failure_threshold
        ):
            logger.warning(
                "model_health_alert",
                model=model_name,
                consecutive_failures=self.stats[
                    model_name
                ].consecutive_failures,
                message=f"模型{model_name}连续失败{self.stats[model_name].consecutive_failures}次",
            )

        return result

    async def check_all_models(self) -> Dict[str, HealthCheckResult]:
        """检查所有已注册模型的健康状态

        Returns:
            Dict[str, HealthCheckResult]: 模型名称到检查结果的映射
        """
        models = [m["name"] for m in self.factory.list_models()]

        if not models:
            logger.info("no_models_to_check")
            return {}

        logger.info("checking_all_models", count=len(models))

        # 并发检查所有模型
        tasks = [self.check_model(model_name) for model_name in models]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        result_dict = {}
        for model_name, result in zip(models, results):
            if isinstance(result, Exception):
                logger.error(
                    "model_check_exception",
                    model=model_name,
                    error=str(result),
                )
                result_dict[model_name] = HealthCheckResult(
                    model_name=model_name,
                    is_healthy=False,
                    response_time=0.0,
                    timestamp=datetime.now(),
                    error=str(result),
                )
            else:
                result_dict[model_name] = result

        return result_dict

    def get_model_stats(
        self, model_name: str, window_minutes: int = 60
    ) -> Optional[Dict[str, Any]]:
        """获取模型的统计信息

        Args:
            model_name: 模型名称
            window_minutes: 时间窗口（分钟）

        Returns:
            统计信息字典，如果模型不存在则返回None
        """
        if model_name not in self.stats:
            return None

        stats = self.stats[model_name]
        overall = stats.get_overall_stats()

        # 添加时间窗口内的统计
        overall["window_minutes"] = window_minutes
        overall["recent_success_rate"] = stats.get_success_rate(
            window_minutes
        )
        overall["recent_avg_response_time"] = (
            stats.get_average_response_time(window_minutes)
        )

        return overall

    def get_all_stats(
        self, window_minutes: int = 60
    ) -> Dict[str, Dict[str, Any]]:
        """获取所有模型的统计信息

        Args:
            window_minutes: 时间窗口（分钟）

        Returns:
            模型名称到统计信息的映射
        """
        return {
            model_name: self.get_model_stats(model_name, window_minutes)
            for model_name in self.stats
        }

    def get_recent_history(
        self, model_name: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取模型的最近检查历史

        Args:
            model_name: 模型名称
            limit: 返回的记录数量

        Returns:
            检查结果列表
        """
        if model_name not in self.stats:
            return []

        history = list(self.stats[model_name].history)
        recent = history[-limit:] if len(history) > limit else history

        return [result.to_dict() for result in reversed(recent)]

    def get_unhealthy_models(self) -> List[str]:
        """获取当前不健康的模型列表

        Returns:
            不健康的模型名称列表
        """
        unhealthy = []
        for model_name, stats in self.stats.items():
            if stats.history and not stats.history[-1].is_healthy:
                unhealthy.append(model_name)

        return unhealthy

    def clear_stats(self, model_name: Optional[str] = None):
        """清空统计信息

        Args:
            model_name: 模型名称，如果为None则清空所有统计
        """
        if model_name:
            if model_name in self.stats:
                del self.stats[model_name]
                logger.info("model_stats_cleared", model=model_name)
        else:
            self.stats.clear()
            logger.info("all_stats_cleared")


# 全局健康检查服务实例
_health_service: Optional[ModelHealthService] = None


def get_health_service(
    factory: Optional[ModelFactory] = None,
) -> ModelHealthService:
    """获取全局健康检查服务实例

    Args:
        factory: 模型工厂实例，首次调用时必须提供

    Returns:
        ModelHealthService: 服务实例
    """
    global _health_service

    if _health_service is None:
        if factory is None:
            raise ValueError("首次调用必须提供factory参数")
        _health_service = ModelHealthService(factory)
        logger.info("health_service_initialized")

    return _health_service
