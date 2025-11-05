"""
测试ModelConfig数据模型和加密功能
"""

import pytest
from uuid import UUID
from datetime import datetime
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from app.models.model_config import (
    ModelConfig,
    ModelConfigCreate,
    ModelConfigUpdate,
    ModelConfigRead,
)
from app.core.crypto import (
    CryptoService,
    encrypt_api_key,
    decrypt_api_key,
)


class TestCryptoService:
    """测试加密服务"""

    def test_crypto_service_initialization(self):
        """测试加密服务初始化"""
        service = CryptoService("test-secret-key")
        assert service is not None
        assert service.fernet is not None

    def test_encrypt_decrypt(self):
        """测试加密和解密"""
        service = CryptoService("test-secret-key")

        plaintext = "sk-1234567890abcdef"
        encrypted = service.encrypt(plaintext)

        # 加密后应该不同
        assert encrypted != plaintext
        assert len(encrypted) > len(plaintext)

        # 解密后应该相同
        decrypted = service.decrypt(encrypted)
        assert decrypted == plaintext

    def test_encrypt_different_each_time(self):
        """测试每次加密结果不同（因为Fernet会添加随机IV）"""
        service = CryptoService("test-secret-key")

        plaintext = "test-api-key"
        encrypted1 = service.encrypt(plaintext)
        encrypted2 = service.encrypt(plaintext)

        # 每次加密结果应该不同
        assert encrypted1 != encrypted2

        # 但都能解密成相同的明文
        assert service.decrypt(encrypted1) == plaintext
        assert service.decrypt(encrypted2) == plaintext

    def test_decrypt_invalid_ciphertext(self):
        """测试解密无效密文"""
        service = CryptoService("test-secret-key")

        with pytest.raises(Exception):
            service.decrypt("invalid-ciphertext")

    def test_encrypt_empty_string(self):
        """测试加密空字符串"""
        service = CryptoService("test-secret-key")

        encrypted = service.encrypt("")
        decrypted = service.decrypt(encrypted)
        assert decrypted == ""

    def test_encrypt_unicode(self):
        """测试加密Unicode字符"""
        service = CryptoService("test-secret-key")

        plaintext = "测试中文密钥🔐"
        encrypted = service.encrypt(plaintext)
        decrypted = service.decrypt(encrypted)
        assert decrypted == plaintext


class TestModelConfigModels:
    """测试ModelConfig相关模型"""

    def test_model_config_base_fields(self):
        """测试ModelConfigCreate的必需字段"""
        config = ModelConfigCreate(
            name="test-model",
            provider="qwen",
            api_base_url="http://test.com/v1",
            api_key="sk-test-key",
            model_version="qwen-turbo",
        )

        assert config.name == "test-model"
        assert config.provider == "qwen"
        assert config.api_base_url == "http://test.com/v1"
        assert config.api_key == "sk-test-key"
        assert config.model_version == "qwen-turbo"
        assert config.max_tokens == 4096  # 默认值
        assert config.temperature == 0.7  # 默认值
        assert config.timeout == 30.0  # 默认值

    def test_model_config_provider_validation(self):
        """测试provider字段的类型验证"""
        # 有效的provider
        for provider in ["qwen", "glm", "deepseek", "vllm", "ollama"]:
            config = ModelConfigCreate(
                name="test",
                provider=provider,
                api_base_url="http://test.com",
                api_key="key",
                model_version="v1",
            )
            assert config.provider == provider

        # 无效的provider应该抛出验证错误
        with pytest.raises(Exception):  # Pydantic验证错误
            ModelConfigCreate(
                name="test",
                provider="invalid-provider",
                api_base_url="http://test.com",
                api_key="key",
                model_version="v1",
            )

    def test_model_config_temperature_validation(self):
        """测试temperature字段的范围验证"""
        # 有效范围内的值
        config = ModelConfigCreate(
            name="test",
            provider="qwen",
            api_base_url="http://test.com",
            api_key="key",
            model_version="v1",
            temperature=1.0,
        )
        assert config.temperature == 1.0

        # 超出范围应该抛出验证错误
        with pytest.raises(Exception):
            ModelConfigCreate(
                name="test",
                provider="qwen",
                api_base_url="http://test.com",
                api_key="key",
                model_version="v1",
                temperature=3.0,  # 超过2.0
            )

    def test_model_config_max_tokens_validation(self):
        """测试max_tokens字段的范围验证"""
        # 有效值
        config = ModelConfigCreate(
            name="test",
            provider="qwen",
            api_base_url="http://test.com",
            api_key="key",
            model_version="v1",
            max_tokens=8192,
        )
        assert config.max_tokens == 8192

        # 小于1应该抛出验证错误
        with pytest.raises(Exception):
            ModelConfigCreate(
                name="test",
                provider="qwen",
                api_base_url="http://test.com",
                api_key="key",
                model_version="v1",
                max_tokens=0,
            )

    def test_model_config_update_partial(self):
        """测试ModelConfigUpdate支持部分更新"""
        update = ModelConfigUpdate(
            temperature=0.8,
            max_tokens=2048,
        )

        assert update.temperature == 0.8
        assert update.max_tokens == 2048
        # 其他字段应该是None
        assert update.name is None
        assert update.provider is None
        assert update.api_key is None

    def test_model_config_update_all_fields(self):
        """测试ModelConfigUpdate可以更新所有字段"""
        update = ModelConfigUpdate(
            name="updated-model",
            provider="deepseek",
            api_base_url="http://new-url.com",
            api_key="new-key",
            model_version="new-version",
            max_tokens=8192,
            temperature=0.5,
            timeout=60.0,
            is_active=False,
            priority=10,
            description="Updated description",
        )

        assert update.name == "updated-model"
        assert update.provider == "deepseek"
        assert update.api_key == "new-key"
        assert update.timeout == 60.0
        assert update.is_active is False

    def test_model_config_read_excludes_sensitive_data(self):
        """测试ModelConfigRead不包含敏感信息"""
        # ModelConfigRead不应该有api_key_encrypted字段
        from pydantic import ValidationError

        # 尝试创建带有敏感字段的读取模型应该失败或被忽略
        # （取决于Pydantic的配置）
        config_data = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "test",
            "provider": "qwen",
            "api_base_url": "http://test.com",
            "model_version": "v1",
            "max_tokens": 4096,
            "temperature": 0.7,
            "is_active": True,
            "priority": 0,
            "timeout": 30.0,
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "last_used_at": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        config = ModelConfigRead(**config_data)
        # 确认没有api_key_encrypted属性
        assert not hasattr(config, "api_key_encrypted")


class TestHelperFunctions:
    """测试辅助函数"""

    def test_encrypt_decrypt_api_key(self):
        """测试API密钥加密解密的便捷函数"""
        api_key = "sk-test-api-key-12345"

        encrypted = encrypt_api_key(api_key)
        assert encrypted != api_key

        decrypted = decrypt_api_key(encrypted)
        assert decrypted == api_key
