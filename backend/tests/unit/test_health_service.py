"""
测试模型健康检查服务
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, AsyncIterator
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from app.services.model_health_service import (
    ModelHealthService,
    HealthCheckResult,
    ModelHealthStats,
)
from model_adapters.model_factory import ModelRegistry, ModelFactory
from model_adapters.base import BaseModelAdapter, ModelResponse


# 测试用虚拟适配器
class HealthyAdapter(BaseModelAdapter):
    """健康的适配器"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.check_delay = 0.1  # 模拟API延迟

    async def chat(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> ModelResponse:
        await asyncio.sleep(self.check_delay)
        return ModelResponse(
            content="OK",
            tokens_used=1,
            cost=0.0,
            model=self.model_name,
            finish_reason="stop",
        )

    async def chat_stream(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> AsyncIterator[str]:
        yield "OK"

    async def health_check(self) -> bool:
        await asyncio.sleep(self.check_delay)
        return True


class UnhealthyAdapter(BaseModelAdapter):
    """不健康的适配器"""

    async def chat(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> ModelResponse:
        raise Exception("Service unavailable")

    async def chat_stream(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> AsyncIterator[str]:
        raise Exception("Service unavailable")

    async def health_check(self) -> bool:
        return False


class TestHealthCheckResult:
    """测试HealthCheckResult"""

    def test_result_creation(self):
        """测试创建结果"""
        timestamp = datetime.now()
        result = HealthCheckResult(
            model_name="test-model",
            is_healthy=True,
            response_time=0.5,
            timestamp=timestamp,
        )

        assert result.model_name == "test-model"
        assert result.is_healthy is True
        assert result.response_time == 0.5
        assert result.timestamp == timestamp
        assert result.error is None

    def test_result_with_error(self):
        """测试带错误的结果"""
        result = HealthCheckResult(
            model_name="test-model",
            is_healthy=False,
            response_time=1.0,
            timestamp=datetime.now(),
            error="Connection timeout",
        )

        assert result.is_healthy is False
        assert result.error == "Connection timeout"

    def test_to_dict(self):
        """测试转换为字典"""
        timestamp = datetime.now()
        result = HealthCheckResult(
            model_name="test-model",
            is_healthy=True,
            response_time=0.5,
            timestamp=timestamp,
        )

        data = result.to_dict()
        assert data["model_name"] == "test-model"
        assert data["is_healthy"] is True
        assert data["response_time"] == 0.5
        assert data["timestamp"] == timestamp.isoformat()


class TestModelHealthStats:
    """测试ModelHealthStats"""

    def test_stats_initialization(self):
        """测试统计初始化"""
        stats = ModelHealthStats("test-model", max_history=50)

        assert stats.model_name == "test-model"
        assert stats.max_history == 50
        assert stats.total_checks == 0
        assert stats.successful_checks == 0
        assert stats.failed_checks == 0

    def test_add_check_result(self):
        """测试添加检查结果"""
        stats = ModelHealthStats("test-model")

        result1 = HealthCheckResult(
            model_name="test-model",
            is_healthy=True,
            response_time=0.5,
            timestamp=datetime.now(),
        )
        stats.add_check_result(result1)

        assert stats.total_checks == 1
        assert stats.successful_checks == 1
        assert stats.failed_checks == 0
        assert stats.consecutive_failures == 0

        result2 = HealthCheckResult(
            model_name="test-model",
            is_healthy=False,
            response_time=1.0,
            timestamp=datetime.now(),
            error="Error",
        )
        stats.add_check_result(result2)

        assert stats.total_checks == 2
        assert stats.successful_checks == 1
        assert stats.failed_checks == 1
        assert stats.consecutive_failures == 1

    def test_consecutive_failures(self):
        """测试连续失败计数"""
        stats = ModelHealthStats("test-model")

        # 添加3个失败结果
        for _ in range(3):
            result = HealthCheckResult(
                model_name="test-model",
                is_healthy=False,
                response_time=1.0,
                timestamp=datetime.now(),
            )
            stats.add_check_result(result)

        assert stats.consecutive_failures == 3

        # 添加一个成功结果
        result = HealthCheckResult(
            model_name="test-model",
            is_healthy=True,
            response_time=0.5,
            timestamp=datetime.now(),
        )
        stats.add_check_result(result)

        assert stats.consecutive_failures == 0

    def test_success_rate(self):
        """测试成功率计算"""
        stats = ModelHealthStats("test-model")

        # 添加检查结果：3成功，1失败
        for i in range(4):
            result = HealthCheckResult(
                model_name="test-model",
                is_healthy=(i != 2),  # 第3个失败
                response_time=0.5,
                timestamp=datetime.now(),
            )
            stats.add_check_result(result)

        success_rate = stats.get_success_rate(window_minutes=60)
        assert success_rate == 0.75  # 3/4

    def test_average_response_time(self):
        """测试平均响应时间计算"""
        stats = ModelHealthStats("test-model")

        # 添加检查结果：0.1, 0.2, 0.3, 0.4
        for i in range(4):
            result = HealthCheckResult(
                model_name="test-model",
                is_healthy=True,
                response_time=(i + 1) * 0.1,
                timestamp=datetime.now(),
            )
            stats.add_check_result(result)

        avg_time = stats.get_average_response_time(window_minutes=60)
        assert abs(avg_time - 0.25) < 0.01  # (0.1+0.2+0.3+0.4)/4 = 0.25

    def test_get_overall_stats(self):
        """测试获取总体统计"""
        stats = ModelHealthStats("test-model")

        result = HealthCheckResult(
            model_name="test-model",
            is_healthy=True,
            response_time=0.5,
            timestamp=datetime.now(),
        )
        stats.add_check_result(result)

        overall = stats.get_overall_stats()

        assert overall["model_name"] == "test-model"
        assert overall["total_checks"] == 1
        assert overall["successful_checks"] == 1
        assert overall["success_rate"] == 1.0
        assert overall["is_currently_healthy"] is True


class TestModelHealthService:
    """测试ModelHealthService"""

    @pytest.fixture
    def factory_with_models(self):
        """创建带模型的工厂"""
        registry = ModelRegistry()
        registry.register("healthy", HealthyAdapter)
        registry.register("unhealthy", UnhealthyAdapter)

        factory = ModelFactory(registry)
        return factory

    @pytest.mark.asyncio
    async def test_service_initialization(self, factory_with_models):
        """测试服务初始化"""
        service = ModelHealthService(
            factory_with_models,
            check_interval=30,
            max_history=50,
            failure_threshold=5,
        )

        assert service.factory == factory_with_models
        assert service.check_interval == 30
        assert service.max_history == 50
        assert service.failure_threshold == 5
        assert not service._running

    @pytest.mark.asyncio
    async def test_check_single_model(self, factory_with_models):
        """测试检查单个模型"""
        # 注册健康模型
        adapter = factory_with_models.create_adapter(
            provider="healthy",
            api_key="test",
            base_url="http://test.com",
            model_name="test-healthy",
        )
        await factory_with_models.register_model("healthy-model", adapter)

        service = ModelHealthService(factory_with_models)
        result = await service.check_model("healthy-model")

        assert result.model_name == "healthy-model"
        assert result.is_healthy is True
        assert result.response_time > 0
        assert result.error is None

    @pytest.mark.asyncio
    async def test_check_unhealthy_model(self, factory_with_models):
        """测试检查不健康的模型"""
        # 注册不健康模型
        adapter = factory_with_models.create_adapter(
            provider="unhealthy",
            api_key="test",
            base_url="http://test.com",
            model_name="test-unhealthy",
        )

        # 手动添加到factory（跳过健康检查）
        factory_with_models._active_models["unhealthy-model"] = adapter

        service = ModelHealthService(factory_with_models)
        result = await service.check_model("unhealthy-model")

        assert result.model_name == "unhealthy-model"
        assert result.is_healthy is False
        assert result.error is None  # health_check返回False，不抛异常

    @pytest.mark.asyncio
    async def test_check_all_models(self, factory_with_models):
        """测试检查所有模型"""
        # 注册两个模型
        healthy_adapter = factory_with_models.create_adapter(
            provider="healthy",
            api_key="test",
            base_url="http://test.com",
            model_name="healthy",
        )
        await factory_with_models.register_model(
            "healthy-model", healthy_adapter
        )

        unhealthy_adapter = factory_with_models.create_adapter(
            provider="unhealthy",
            api_key="test",
            base_url="http://test.com",
            model_name="unhealthy",
        )
        # 手动添加到factory（跳过健康检查）
        factory_with_models._active_models["unhealthy-model"] = (
            unhealthy_adapter
        )
        factory_with_models._model_metadata["unhealthy-model"] = {
            "provider": "UnhealthyAdapter",
            "model_name": "unhealthy",
        }

        service = ModelHealthService(factory_with_models)
        results = await service.check_all_models()

        assert len(results) == 2
        assert "healthy-model" in results
        assert "unhealthy-model" in results
        assert results["healthy-model"].is_healthy is True
        assert results["unhealthy-model"].is_healthy is False

    @pytest.mark.asyncio
    async def test_stats_tracking(self, factory_with_models):
        """测试统计追踪"""
        adapter = factory_with_models.create_adapter(
            provider="healthy",
            api_key="test",
            base_url="http://test.com",
            model_name="test",
        )
        await factory_with_models.register_model("test-model", adapter)

        service = ModelHealthService(factory_with_models)

        # 执行3次检查
        for _ in range(3):
            await service.check_model("test-model")

        stats = service.get_model_stats("test-model")
        assert stats is not None
        assert stats["total_checks"] == 3
        assert stats["successful_checks"] == 3
        assert stats["success_rate"] == 1.0

    @pytest.mark.asyncio
    async def test_failure_threshold_alert(self, factory_with_models):
        """测试失败阈值告警"""
        adapter = factory_with_models.create_adapter(
            provider="unhealthy",
            api_key="test",
            base_url="http://test.com",
            model_name="test",
        )
        factory_with_models._active_models["test-model"] = adapter

        service = ModelHealthService(
            factory_with_models, failure_threshold=3
        )

        # 执行3次检查，应该触发告警
        for _ in range(3):
            await service.check_model("test-model")

        stats = service.stats["test-model"]
        assert stats.consecutive_failures == 3

    @pytest.mark.asyncio
    async def test_get_recent_history(self, factory_with_models):
        """测试获取最近历史"""
        adapter = factory_with_models.create_adapter(
            provider="healthy",
            api_key="test",
            base_url="http://test.com",
            model_name="test",
        )
        await factory_with_models.register_model("test-model", adapter)

        service = ModelHealthService(factory_with_models)

        # 执行5次检查
        for _ in range(5):
            await service.check_model("test-model")

        history = service.get_recent_history("test-model", limit=3)
        assert len(history) == 3

        # 验证是按时间倒序
        timestamps = [h["timestamp"] for h in history]
        assert timestamps == sorted(timestamps, reverse=True)

    @pytest.mark.asyncio
    async def test_get_unhealthy_models(self, factory_with_models):
        """测试获取不健康的模型"""
        healthy_adapter = factory_with_models.create_adapter(
            provider="healthy",
            api_key="test",
            base_url="http://test.com",
            model_name="healthy",
        )
        await factory_with_models.register_model(
            "healthy-model", healthy_adapter
        )

        unhealthy_adapter = factory_with_models.create_adapter(
            provider="unhealthy",
            api_key="test",
            base_url="http://test.com",
            model_name="unhealthy",
        )
        # 手动添加到factory（跳过健康检查）
        factory_with_models._active_models["unhealthy-model"] = (
            unhealthy_adapter
        )
        factory_with_models._model_metadata["unhealthy-model"] = {
            "provider": "UnhealthyAdapter",
            "model_name": "unhealthy",
        }

        service = ModelHealthService(factory_with_models)
        await service.check_all_models()

        unhealthy = service.get_unhealthy_models()
        assert "unhealthy-model" in unhealthy
        assert "healthy-model" not in unhealthy

    @pytest.mark.asyncio
    async def test_clear_stats(self, factory_with_models):
        """测试清空统计"""
        adapter = factory_with_models.create_adapter(
            provider="healthy",
            api_key="test",
            base_url="http://test.com",
            model_name="test",
        )
        await factory_with_models.register_model("test-model", adapter)

        service = ModelHealthService(factory_with_models)
        await service.check_model("test-model")

        assert "test-model" in service.stats

        service.clear_stats("test-model")
        assert "test-model" not in service.stats

    @pytest.mark.asyncio
    async def test_start_stop_service(self, factory_with_models):
        """测试启动和停止服务"""
        adapter = factory_with_models.create_adapter(
            provider="healthy",
            api_key="test",
            base_url="http://test.com",
            model_name="test",
        )
        await factory_with_models.register_model("test-model", adapter)

        service = ModelHealthService(
            factory_with_models, check_interval=1
        )

        # 启动服务
        await service.start()
        assert service._running is True
        assert service._check_task is not None

        # 等待一段时间让它执行检查
        await asyncio.sleep(1.5)

        # 应该至少执行了一次检查
        assert "test-model" in service.stats
        assert service.stats["test-model"].total_checks >= 1

        # 停止服务
        await service.stop()
        assert service._running is False
