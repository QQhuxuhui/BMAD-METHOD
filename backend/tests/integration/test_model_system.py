"""
模型系统集成测试

测试模型适配器、工厂、配置加载器等组件的集成。
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from model_adapters.qwen_adapter import QwenAdapter
from model_adapters.deepseek_adapter import DeepSeekAdapter
from model_adapters.model_factory import ModelFactory
from model_adapters.config_loader import ModelConfigLoader


class TestModelSystemIntegration:
    """测试模型系统的集成"""

    @pytest.mark.asyncio
    async def test_factory_register_and_get_model(self):
        """测试工厂注册和获取模型的完整流程"""
        factory = ModelFactory()

        # 创建一个模拟适配器
        mock_adapter = AsyncMock(spec=QwenAdapter)
        mock_adapter.health_check = AsyncMock(return_value=True)
        mock_adapter.model_name = "qwen-test"
        mock_adapter.base_url = "http://test.com"

        # 注册模型
        await factory.register_model("test-qwen", mock_adapter, set_as_default=True)

        # 获取模型（非异步方法）
        retrieved = factory.get_model("test-qwen")
        assert retrieved is mock_adapter

        # 获取默认模型（非异步方法）
        default = factory.get_model()  # 不传参数获取默认模型
        assert default is mock_adapter

        # 列出所有模型
        models = factory.list_models()
        assert len(models) == 1
        assert models[0]["name"] == "test-qwen"
        assert models[0]["is_default"] is True

    @pytest.mark.asyncio
    async def test_factory_hot_switch(self):
        """测试工厂热切换功能"""
        factory = ModelFactory()

        # 创建两个模拟适配器
        mock_qwen = AsyncMock(spec=QwenAdapter)
        mock_qwen.health_check = AsyncMock(return_value=True)
        mock_qwen.model_name = "qwen"
        mock_qwen.base_url = "http://test.com"

        mock_deepseek = AsyncMock(spec=DeepSeekAdapter)
        mock_deepseek.health_check = AsyncMock(return_value=True)
        mock_deepseek.model_name = "deepseek"
        mock_deepseek.base_url = "http://test.com"

        # 注册两个模型
        await factory.register_model("qwen", mock_qwen, set_as_default=True)
        await factory.register_model("deepseek", mock_deepseek)

        # 验证初始默认模型（非异步方法）
        default = factory.get_model()  # 不传参数获取默认模型
        assert default is mock_qwen

        # 切换默认模型
        await factory.switch_model("deepseek")

        # 验证切换后的默认模型（非异步方法）
        default = factory.get_model()
        assert default is mock_deepseek

    @pytest.mark.asyncio
    @patch("model_adapters.config_loader.settings")
    async def test_config_loader_and_factory_integration(self, mock_settings):
        """测试配置加载器与工厂的集成"""
        # 配置mock settings
        mock_settings.QWEN_API_KEY = "test-qwen-key"
        mock_settings.QWEN_API_BASE_URL = "http://test-qwen.com/v1"
        mock_settings.QWEN_MODEL_VERSION = "qwen-test"
        mock_settings.QWEN_MAX_TOKENS = 2048
        mock_settings.QWEN_TEMPERATURE = 0.5
        mock_settings.MODEL_DEFAULT_TIMEOUT = 30.0
        mock_settings.DEFAULT_MODEL_PROVIDER = "qwen"

        mock_settings.DEEPSEEK_API_KEY = ""  # 不配置DeepSeek

        # 创建配置加载器
        loader = ModelConfigLoader()

        # 从环境变量加载
        adapters = loader.load_from_env()

        # 应该只加载Qwen
        assert "qwen" in adapters
        assert isinstance(adapters["qwen"], QwenAdapter)
        assert len(adapters) == 1

    @pytest.mark.asyncio
    async def test_factory_with_unhealthy_model(self):
        """测试工厂处理不健康的模型"""
        factory = ModelFactory()

        # 创建一个不健康的适配器
        unhealthy_adapter = AsyncMock(spec=QwenAdapter)
        unhealthy_adapter.health_check = AsyncMock(return_value=False)
        unhealthy_adapter.model_name = "unhealthy-model"
        unhealthy_adapter.base_url = "http://test.com"

        # 尝试注册不健康的模型应该失败
        with pytest.raises(Exception):  # 应该抛出健康检查失败的异常
            await factory.register_model("unhealthy", unhealthy_adapter)

    def test_factory_model_not_found(self):
        """测试获取不存在的模型"""
        from model_adapters.exceptions import ModelConfigurationError

        factory = ModelFactory()

        # 获取不存在的模型应该抛出异常
        with pytest.raises(ModelConfigurationError):
            factory.get_model("nonexistent")

    @pytest.mark.asyncio
    async def test_factory_multiple_models_listing(self):
        """测试列出多个模型"""
        factory = ModelFactory()

        # 创建多个模拟适配器
        adapters = {}
        for i in range(3):
            mock_adapter = AsyncMock()
            mock_adapter.health_check = AsyncMock(return_value=True)
            mock_adapter.model_name = f"model-{i}"
            mock_adapter.base_url = "http://test.com"
            adapters[f"model-{i}"] = mock_adapter

            await factory.register_model(
                f"model-{i}",
                mock_adapter,
                set_as_default=(i == 0),
            )

        # 列出所有模型
        models = factory.list_models()
        assert len(models) == 3

        # 验证默认模型
        default_models = [m for m in models if m["is_default"]]
        assert len(default_models) == 1
        assert default_models[0]["name"] == "model-0"


class TestAdapterIntegration:
    """测试适配器之间的集成"""

    def test_qwen_and_deepseek_adapters_compatibility(self):
        """测试Qwen和DeepSeek适配器的兼容性"""
        qwen = QwenAdapter(
            api_key="test-key",
            base_url="http://test.com/v1",
            model_name="qwen-test",
        )

        deepseek = DeepSeekAdapter(
            api_key="test-key",
            base_url="http://test.com/v1",
            model_name="deepseek-test",
        )

        # 两个适配器应该有相同的接口
        assert hasattr(qwen, "chat")
        assert hasattr(qwen, "chat_stream")
        assert hasattr(qwen, "health_check")

        assert hasattr(deepseek, "chat")
        assert hasattr(deepseek, "chat_stream")
        assert hasattr(deepseek, "health_check")

        # 两个适配器的配置应该独立
        assert qwen.model_name == "qwen-test"
        assert deepseek.model_name == "deepseek-test"
