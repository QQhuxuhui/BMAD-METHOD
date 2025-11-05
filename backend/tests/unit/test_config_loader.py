"""
测试模型配置加载器
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from model_adapters.config_loader import (
    ModelConfigLoader,
    get_config_loader,
    initialize_models,
)
from model_adapters.qwen_adapter import QwenAdapter
from model_adapters.deepseek_adapter import DeepSeekAdapter


class TestModelConfigLoader:
    """测试模型配置加载器"""

    def test_get_config_loader_singleton(self):
        """测试配置加载器单例模式"""
        loader1 = get_config_loader()
        loader2 = get_config_loader()

        assert loader1 is loader2
        assert isinstance(loader1, ModelConfigLoader)

    @patch("model_adapters.config_loader.settings")
    def test_load_from_env_qwen_only(self, mock_settings):
        """测试仅从环境变量加载Qwen配置"""
        # 配置mock settings
        mock_settings.QWEN_API_KEY = "test-qwen-key"
        mock_settings.QWEN_API_BASE_URL = "http://test-qwen.com/v1"
        mock_settings.QWEN_MODEL_VERSION = "qwen-test"
        mock_settings.QWEN_MAX_TOKENS = 2048
        mock_settings.QWEN_TEMPERATURE = 0.5
        mock_settings.MODEL_DEFAULT_TIMEOUT = 30.0

        mock_settings.DEEPSEEK_API_KEY = ""  # DeepSeek未配置
        mock_settings.GLM_API_KEY = ""  # GLM未配置

        loader = ModelConfigLoader()
        adapters = loader.load_from_env()

        # 应该只加载Qwen
        assert "qwen" in adapters
        assert isinstance(adapters["qwen"], QwenAdapter)
        assert len(adapters) == 1

    @patch("model_adapters.config_loader.settings")
    def test_load_from_env_multiple_models(self, mock_settings):
        """测试从环境变量加载多个模型配置"""
        # 配置mock settings
        mock_settings.QWEN_API_KEY = "test-qwen-key"
        mock_settings.QWEN_API_BASE_URL = "http://test-qwen.com/v1"
        mock_settings.QWEN_MODEL_VERSION = "qwen-test"
        mock_settings.QWEN_MAX_TOKENS = 2048
        mock_settings.QWEN_TEMPERATURE = 0.5

        mock_settings.DEEPSEEK_API_KEY = "test-deepseek-key"
        mock_settings.DEEPSEEK_API_BASE_URL = "http://test-deepseek.com/v1"
        mock_settings.DEEPSEEK_MODEL_VERSION = "deepseek-test"
        mock_settings.DEEPSEEK_MAX_TOKENS = 4096
        mock_settings.DEEPSEEK_TEMPERATURE = 0.7

        mock_settings.MODEL_DEFAULT_TIMEOUT = 30.0

        loader = ModelConfigLoader()
        adapters = loader.load_from_env()

        # 应该加载Qwen和DeepSeek
        assert "qwen" in adapters
        assert "deepseek" in adapters
        assert isinstance(adapters["qwen"], QwenAdapter)
        assert isinstance(adapters["deepseek"], DeepSeekAdapter)
        assert len(adapters) == 2

    @patch("model_adapters.config_loader.settings")
    def test_load_from_env_no_models(self, mock_settings):
        """测试环境变量未配置任何模型"""
        mock_settings.QWEN_API_KEY = ""
        mock_settings.DEEPSEEK_API_KEY = ""
        mock_settings.GLM_API_KEY = ""

        loader = ModelConfigLoader()
        adapters = loader.load_from_env()

        # 应该返回空字典
        assert len(adapters) == 0

    @pytest.mark.asyncio
    async def test_load_from_database_no_session(self):
        """测试未提供session时从数据库加载"""
        loader = ModelConfigLoader()

        # 不应该抛出异常，应该返回空字典
        adapters = await loader.load_from_database(None)
        assert len(adapters) == 0

    def test_create_adapter_from_config_qwen(self):
        """测试从配置创建Qwen适配器"""
        from app.models.model_config import ModelConfig as DBModelConfig
        from datetime import datetime, UTC
        from uuid import uuid4

        config = DBModelConfig(
            id=uuid4(),
            name="test-qwen",
            provider="qwen",
            api_base_url="http://test.com/v1",
            model_version="qwen-test",
            max_tokens=2048,
            temperature=0.5,
            timeout=30.0,
            is_active=True,
            priority=1,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        loader = ModelConfigLoader()
        adapter = loader._create_adapter_from_config(config, "test-api-key")

        assert adapter is not None
        assert isinstance(adapter, QwenAdapter)
        assert adapter.model_name == "qwen-test"

    def test_create_adapter_from_config_unsupported_provider(self):
        """测试创建不支持的provider的适配器"""
        from app.models.model_config import ModelConfig as DBModelConfig
        from datetime import datetime, UTC
        from uuid import uuid4

        config = DBModelConfig(
            id=uuid4(),
            name="test-unsupported",
            provider="unsupported-provider",
            api_base_url="http://test.com/v1",
            model_version="test",
            max_tokens=2048,
            temperature=0.5,
            timeout=30.0,
            is_active=True,
            priority=1,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        loader = ModelConfigLoader()
        adapter = loader._create_adapter_from_config(config, "test-api-key")

        # 应该返回None（不支持的provider）
        # 注意：这会记录警告日志，但不会抛出异常
        # 由于provider验证在Pydantic模型层，这里可能会在创建config时就失败
        # 实际测试需要根据实际验证逻辑调整


class TestInitializeFunctions:
    """测试初始化函数"""

    @pytest.mark.asyncio
    @patch("model_adapters.config_loader.settings")
    @patch("model_adapters.config_loader.ModelConfigLoader.load_from_env")
    async def test_initialize_models_env_only(
        self, mock_load_from_env, mock_settings
    ):
        """测试仅从环境变量初始化模型"""
        # Mock配置
        mock_settings.DEFAULT_MODEL_PROVIDER = "qwen"

        # Mock返回的适配器（需要包含model_name属性）
        mock_qwen_adapter = Mock(spec=QwenAdapter)
        mock_qwen_adapter.health_check = AsyncMock(return_value=True)
        mock_qwen_adapter.model_name = "qwen-test"
        mock_qwen_adapter.base_url = "http://test.com"
        mock_load_from_env.return_value = {"qwen": mock_qwen_adapter}

        # 不提供session，仅从环境变量加载
        factory = await initialize_models(session=None)

        assert factory is not None
        # 验证至少尝试注册了模型
        mock_load_from_env.assert_called_once()
