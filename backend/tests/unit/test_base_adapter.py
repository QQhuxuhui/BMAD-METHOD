"""
测试BaseModelAdapter基类和相关组件
"""

import pytest
from typing import List, Dict, AsyncIterator
import sys
from pathlib import Path

# 添加backend目录到Python路径
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from model_adapters.base import BaseModelAdapter, ModelResponse
from model_adapters.config import ModelConfig, CostConfig, DEFAULT_COST_CONFIGS
from model_adapters.exceptions import (
    ModelAdapterError,
    ModelUnavailableError,
    ModelTimeoutError,
    ModelQuotaExceededError,
    ModelConfigurationError,
    ModelResponseError,
)


# 创建用于测试的具体适配器实现
class DummyAdapter(BaseModelAdapter):
    """用于测试的虚拟适配器"""

    async def chat(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> ModelResponse:
        return ModelResponse(
            content="Test response",
            tokens_used=10,
            cost=0.001,
            model=self.model_name,
            finish_reason="stop",
        )

    async def chat_stream(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> AsyncIterator[str]:
        tokens = ["Hello", " ", "world", "!"]
        for token in tokens:
            yield token

    async def health_check(self) -> bool:
        return True


class TestModelResponse:
    """测试ModelResponse数据模型"""

    def test_model_response_creation(self):
        """测试ModelResponse正常创建"""
        response = ModelResponse(
            content="Hello",
            tokens_used=5,
            cost=0.001,
            model="test-model",
            finish_reason="stop",
        )
        assert response.content == "Hello"
        assert response.tokens_used == 5
        assert response.cost == 0.001
        assert response.model == "test-model"
        assert response.finish_reason == "stop"
        assert response.metadata is None

    def test_model_response_with_metadata(self):
        """测试带metadata的ModelResponse"""
        metadata = {"latency": 100, "region": "us-east-1"}
        response = ModelResponse(
            content="Hello",
            tokens_used=5,
            cost=0.001,
            model="test-model",
            finish_reason="stop",
            metadata=metadata,
        )
        assert response.metadata == metadata


class TestBaseModelAdapter:
    """测试BaseModelAdapter基类"""

    def test_adapter_initialization(self):
        """测试适配器初始化"""
        adapter = DummyAdapter(
            api_key="test-key",
            base_url="https://api.test.com",
            model_name="test-model",
            max_tokens=2000,
            temperature=0.8,
        )
        assert adapter.api_key == "test-key"
        assert adapter.base_url == "https://api.test.com"
        assert adapter.model_name == "test-model"
        assert adapter.max_tokens == 2000
        assert adapter.temperature == 0.8

    @pytest.mark.asyncio
    async def test_chat_method(self):
        """测试chat方法"""
        adapter = DummyAdapter(
            api_key="test-key",
            base_url="https://api.test.com",
            model_name="test-model",
        )
        messages = [{"role": "user", "content": "Hello"}]
        response = await adapter.chat(messages)

        assert isinstance(response, ModelResponse)
        assert response.content == "Test response"
        assert response.tokens_used == 10
        assert response.model == "test-model"

    @pytest.mark.asyncio
    async def test_chat_stream_method(self):
        """测试chat_stream方法"""
        adapter = DummyAdapter(
            api_key="test-key",
            base_url="https://api.test.com",
            model_name="test-model",
        )
        messages = [{"role": "user", "content": "Hello"}]

        chunks = []
        async for chunk in adapter.chat_stream(messages):
            chunks.append(chunk)

        assert chunks == ["Hello", " ", "world", "!"]

    @pytest.mark.asyncio
    async def test_health_check_method(self):
        """测试health_check方法"""
        adapter = DummyAdapter(
            api_key="test-key",
            base_url="https://api.test.com",
            model_name="test-model",
        )
        is_healthy = await adapter.health_check()
        assert is_healthy is True

    def test_calculate_cost_default(self):
        """测试默认的calculate_cost方法"""
        adapter = DummyAdapter(
            api_key="test-key",
            base_url="https://api.test.com",
            model_name="test-model",
        )
        cost = adapter.calculate_cost(1000)
        assert cost == 0.0

    def test_build_headers(self):
        """测试_build_headers方法"""
        adapter = DummyAdapter(
            api_key="test-key",
            base_url="https://api.test.com",
            model_name="test-model",
        )
        headers = adapter._build_headers()
        assert headers["Authorization"] == "Bearer test-key"
        assert headers["Content-Type"] == "application/json"

    def test_prepare_messages(self):
        """测试_prepare_messages方法"""
        adapter = DummyAdapter(
            api_key="test-key",
            base_url="https://api.test.com",
            model_name="test-model",
        )
        messages = [{"role": "user", "content": "Hello"}]
        prepared = adapter._prepare_messages(messages)
        assert prepared == messages

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """测试异步上下文管理器"""
        async with DummyAdapter(
            api_key="test-key",
            base_url="https://api.test.com",
            model_name="test-model",
        ) as adapter:
            assert isinstance(adapter, DummyAdapter)


class TestModelConfig:
    """测试ModelConfig配置模型"""

    def test_model_config_creation(self):
        """测试ModelConfig正常创建"""
        config = ModelConfig(
            name="test-config",
            provider="qwen",
            api_key="test-key",
            api_base_url="https://api.test.com",
            model_version="qwen-turbo",
        )
        assert config.name == "test-config"
        assert config.provider == "qwen"
        assert config.max_tokens == 4096  # 默认值
        assert config.temperature == 0.7  # 默认值
        assert config.is_active is True

    def test_model_config_validation(self):
        """测试ModelConfig参数验证"""
        with pytest.raises(Exception):  # temperature超出范围
            ModelConfig(
                name="test",
                provider="qwen",
                api_key="key",
                api_base_url="url",
                model_version="v1",
                temperature=3.0,  # 超过最大值2.0
            )

    def test_model_config_with_extra_params(self):
        """测试带额外参数的ModelConfig"""
        config = ModelConfig(
            name="test",
            provider="qwen",
            api_key="key",
            api_base_url="url",
            model_version="v1",
            extra_params={"top_p": 0.9, "frequency_penalty": 0.5},
        )
        assert config.extra_params["top_p"] == 0.9


class TestCostConfig:
    """测试CostConfig计费配置"""

    def test_cost_calculation(self):
        """测试成本计算"""
        cost_config = CostConfig(
            input_price_per_1k=0.001, output_price_per_1k=0.002
        )
        total_cost = cost_config.calculate_cost(
            input_tokens=1000, output_tokens=500
        )
        # 输入: 1000/1000 * 0.001 = 0.001
        # 输出: 500/1000 * 0.002 = 0.001
        # 总计: 0.002
        assert total_cost == pytest.approx(0.002)

    def test_default_cost_configs(self):
        """测试预定义的成本配置"""
        assert "qwen-turbo" in DEFAULT_COST_CONFIGS
        assert "glm-4" in DEFAULT_COST_CONFIGS
        assert "deepseek-chat" in DEFAULT_COST_CONFIGS
        assert "local" in DEFAULT_COST_CONFIGS

        # 验证本地模型成本为0
        local_cost = DEFAULT_COST_CONFIGS["local"]
        assert local_cost.calculate_cost(1000, 1000) == 0.0


class TestExceptions:
    """测试自定义异常"""

    def test_base_exception(self):
        """测试基础异常"""
        with pytest.raises(ModelAdapterError):
            raise ModelAdapterError("Test error")

    def test_unavailable_exception(self):
        """测试服务不可用异常"""
        with pytest.raises(ModelUnavailableError):
            raise ModelUnavailableError("Service down")

    def test_timeout_exception(self):
        """测试超时异常"""
        with pytest.raises(ModelTimeoutError):
            raise ModelTimeoutError("Request timeout")

    def test_quota_exception(self):
        """测试配额超限异常"""
        with pytest.raises(ModelQuotaExceededError):
            raise ModelQuotaExceededError("Quota exceeded")

    def test_configuration_exception(self):
        """测试配置错误异常"""
        with pytest.raises(ModelConfigurationError):
            raise ModelConfigurationError("Invalid config")

    def test_response_exception(self):
        """测试响应错误异常"""
        with pytest.raises(ModelResponseError):
            raise ModelResponseError("Invalid response")

    def test_exception_inheritance(self):
        """测试异常继承关系"""
        assert issubclass(ModelUnavailableError, ModelAdapterError)
        assert issubclass(ModelTimeoutError, ModelAdapterError)
        assert issubclass(ModelQuotaExceededError, ModelAdapterError)
