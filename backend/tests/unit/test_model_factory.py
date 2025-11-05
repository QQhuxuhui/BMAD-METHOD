"""
测试模型工厂和注册表
"""

import pytest
from typing import List, Dict, AsyncIterator
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from model_adapters.model_factory import ModelRegistry, ModelFactory
from model_adapters.base import BaseModelAdapter, ModelResponse
from model_adapters.config import ModelConfig
from model_adapters.exceptions import ModelConfigurationError


# 创建用于测试的虚拟适配器
class DummyAdapter(BaseModelAdapter):
    """测试用虚拟适配器"""

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
        for token in ["Hello", " ", "World"]:
            yield token

    async def health_check(self) -> bool:
        return True


class UnhealthyAdapter(BaseModelAdapter):
    """测试用不健康的适配器"""

    async def chat(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> ModelResponse:
        return ModelResponse(
            content="Test",
            tokens_used=1,
            cost=0,
            model=self.model_name,
            finish_reason="stop",
        )

    async def chat_stream(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> AsyncIterator[str]:
        yield "Test"

    async def health_check(self) -> bool:
        return False


class TestModelRegistry:
    """测试模型注册表"""

    def test_registry_initialization(self):
        """测试注册表初始化"""
        registry = ModelRegistry()
        assert registry.list_providers() == []

    def test_register_provider(self):
        """测试注册提供商"""
        registry = ModelRegistry()
        registry.register("test", DummyAdapter)

        assert registry.is_registered("test")
        assert "test" in registry.list_providers()
        assert registry.get("test") == DummyAdapter

    def test_register_duplicate_provider(self):
        """测试重复注册提供商（应该覆盖）"""
        registry = ModelRegistry()
        registry.register("test", DummyAdapter)
        registry.register("test", UnhealthyAdapter)

        # 第二次注册应该覆盖第一次
        assert registry.get("test") == UnhealthyAdapter

    def test_unregister_provider(self):
        """测试注销提供商"""
        registry = ModelRegistry()
        registry.register("test", DummyAdapter)
        assert registry.is_registered("test")

        registry.unregister("test")
        assert not registry.is_registered("test")
        assert registry.get("test") is None

    def test_get_nonexistent_provider(self):
        """测试获取不存在的提供商"""
        registry = ModelRegistry()
        assert registry.get("nonexistent") is None

    def test_thread_safety(self):
        """测试线程安全（简单测试）"""
        import threading

        registry = ModelRegistry()
        errors = []

        def register_provider(name):
            try:
                registry.register(name, DummyAdapter)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=register_provider, args=(f"test{i}",))
            for i in range(10)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(registry.list_providers()) == 10


class TestModelFactory:
    """测试模型工厂"""

    def test_factory_initialization(self):
        """测试工厂初始化"""
        factory = ModelFactory()
        assert factory.registry is not None
        assert factory.list_models() == []
        assert factory.get_default_model_name() is None

    def test_factory_with_custom_registry(self):
        """测试使用自定义注册表初始化工厂"""
        registry = ModelRegistry()
        registry.register("test", DummyAdapter)

        factory = ModelFactory(registry)
        assert factory.registry.is_registered("test")

    def test_create_adapter_success(self):
        """测试创建适配器成功"""
        registry = ModelRegistry()
        registry.register("dummy", DummyAdapter)
        factory = ModelFactory(registry)

        adapter = factory.create_adapter(
            provider="dummy",
            api_key="test-key",
            base_url="http://test.com",
            model_name="test-model",
        )

        assert isinstance(adapter, DummyAdapter)
        assert adapter.api_key == "test-key"
        assert adapter.base_url == "http://test.com"
        assert adapter.model_name == "test-model"

    def test_create_adapter_unregistered_provider(self):
        """测试创建未注册提供商的适配器"""
        factory = ModelFactory()

        with pytest.raises(ModelConfigurationError):
            factory.create_adapter(
                provider="nonexistent",
                api_key="test",
                base_url="http://test.com",
                model_name="test",
            )

    def test_create_from_config(self):
        """测试从配置创建适配器"""
        registry = ModelRegistry()
        registry.register("qwen", DummyAdapter)  # 使用有效的provider
        factory = ModelFactory(registry)

        config = ModelConfig(
            name="test-config",
            provider="qwen",  # 使用有效的provider值
            api_key="test-key",
            api_base_url="http://test.com",
            model_version="test-model",
            max_tokens=2000,
        )

        adapter = factory.create_from_config(config)
        assert isinstance(adapter, DummyAdapter)
        assert adapter.model_name == "test-model"
        assert adapter.max_tokens == 2000

    @pytest.mark.asyncio
    async def test_register_model_success(self):
        """测试注册模型成功"""
        registry = ModelRegistry()
        registry.register("dummy", DummyAdapter)
        factory = ModelFactory(registry)

        adapter = factory.create_adapter(
            provider="dummy",
            api_key="test",
            base_url="http://test.com",
            model_name="test-model",
        )

        await factory.register_model("model1", adapter)

        assert factory.has_model("model1")
        assert factory.get_default_model_name() == "model1"

    @pytest.mark.asyncio
    async def test_register_unhealthy_model(self):
        """测试注册不健康的模型"""
        registry = ModelRegistry()
        registry.register("unhealthy", UnhealthyAdapter)
        factory = ModelFactory(registry)

        adapter = factory.create_adapter(
            provider="unhealthy",
            api_key="test",
            base_url="http://test.com",
            model_name="test",
        )

        with pytest.raises(ModelConfigurationError):
            await factory.register_model("unhealthy_model", adapter)

    @pytest.mark.asyncio
    async def test_register_multiple_models(self):
        """测试注册多个模型"""
        registry = ModelRegistry()
        registry.register("dummy", DummyAdapter)
        factory = ModelFactory(registry)

        adapter1 = factory.create_adapter(
            provider="dummy",
            api_key="test",
            base_url="http://test.com",
            model_name="model1",
        )
        adapter2 = factory.create_adapter(
            provider="dummy",
            api_key="test",
            base_url="http://test.com",
            model_name="model2",
        )

        await factory.register_model("model1", adapter1)
        await factory.register_model("model2", adapter2, set_as_default=False)

        assert factory.has_model("model1")
        assert factory.has_model("model2")
        assert factory.get_default_model_name() == "model1"  # 第一个是默认

    def test_unregister_model(self):
        """测试注销模型"""
        registry = ModelRegistry()
        registry.register("dummy", DummyAdapter)
        factory = ModelFactory(registry)

        adapter = factory.create_adapter(
            provider="dummy",
            api_key="test",
            base_url="http://test.com",
            model_name="test",
        )

        # 需要异步注册，这里简化测试
        factory._active_models["model1"] = adapter
        factory._model_metadata["model1"] = {}
        factory._default_model = "model1"

        factory.unregister_model("model1")

        assert not factory.has_model("model1")
        assert factory.get_default_model_name() is None

    def test_get_model(self):
        """测试获取模型"""
        registry = ModelRegistry()
        registry.register("dummy", DummyAdapter)
        factory = ModelFactory(registry)

        adapter = factory.create_adapter(
            provider="dummy",
            api_key="test",
            base_url="http://test.com",
            model_name="test",
        )

        factory._active_models["model1"] = adapter
        factory._default_model = "model1"

        retrieved = factory.get_model("model1")
        assert retrieved == adapter

        # 测试获取默认模型
        default = factory.get_model()
        assert default == adapter

    def test_get_nonexistent_model(self):
        """测试获取不存在的模型"""
        factory = ModelFactory()

        with pytest.raises(ModelConfigurationError):
            factory.get_model("nonexistent")

    @pytest.mark.asyncio
    async def test_switch_model(self):
        """测试切换模型"""
        registry = ModelRegistry()
        registry.register("dummy", DummyAdapter)
        factory = ModelFactory(registry)

        adapter1 = factory.create_adapter(
            provider="dummy",
            api_key="test",
            base_url="http://test.com",
            model_name="model1",
        )
        adapter2 = factory.create_adapter(
            provider="dummy",
            api_key="test",
            base_url="http://test.com",
            model_name="model2",
        )

        await factory.register_model("model1", adapter1)
        await factory.register_model("model2", adapter2, set_as_default=False)

        assert factory.get_default_model_name() == "model1"

        # 切换到model2
        await factory.switch_model("model2")
        assert factory.get_default_model_name() == "model2"

    def test_list_models(self):
        """测试列出所有模型"""
        registry = ModelRegistry()
        registry.register("dummy", DummyAdapter)
        factory = ModelFactory(registry)

        adapter = factory.create_adapter(
            provider="dummy",
            api_key="test",
            base_url="http://test.com",
            model_name="test",
        )

        factory._active_models["model1"] = adapter
        factory._model_metadata["model1"] = {
            "provider": "DummyAdapter",
            "model_name": "test",
        }
        factory._default_model = "model1"

        models = factory.list_models()
        assert len(models) == 1
        assert models[0]["name"] == "model1"
        assert models[0]["is_default"] is True

    @pytest.mark.asyncio
    async def test_health_check_all(self):
        """测试批量健康检查"""
        registry = ModelRegistry()
        registry.register("dummy", DummyAdapter)
        factory = ModelFactory(registry)

        adapter1 = factory.create_adapter(
            provider="dummy",
            api_key="test",
            base_url="http://test.com",
            model_name="model1",
        )
        adapter2 = factory.create_adapter(
            provider="dummy",
            api_key="test",
            base_url="http://test.com",
            model_name="model2",
        )

        await factory.register_model("model1", adapter1)
        await factory.register_model("model2", adapter2)

        results = await factory.health_check_all()

        assert results["model1"] is True
        assert results["model2"] is True
