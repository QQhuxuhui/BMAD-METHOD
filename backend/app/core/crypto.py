"""
加密工具

用于加密和解密敏感信息（如API密钥）。
"""

import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import structlog

logger = structlog.get_logger(__name__)


class CryptoService:
    """加密服务

    使用Fernet（对称加密）来加密和解密敏感数据。
    """

    def __init__(self, secret_key: str):
        """初始化加密服务

        Args:
            secret_key: 用于加密的密钥（建议从环境变量读取）
        """
        # 使用PBKDF2HMAC从密钥派生出Fernet所需的32字节密钥
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"bmad-method-salt",  # 在生产环境应该使用随机salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))
        self.fernet = Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        """加密文本

        Args:
            plaintext: 明文

        Returns:
            加密后的文本（Base64编码）
        """
        try:
            encrypted_bytes = self.fernet.encrypt(plaintext.encode())
            return encrypted_bytes.decode()
        except Exception as e:
            logger.error("encryption_failed", error=str(e))
            raise

    def decrypt(self, ciphertext: str) -> str:
        """解密文本

        Args:
            ciphertext: 密文（Base64编码）

        Returns:
            解密后的明文
        """
        try:
            decrypted_bytes = self.fernet.decrypt(ciphertext.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            logger.error("decryption_failed", error=str(e))
            raise


# 全局加密服务实例
_crypto_service: CryptoService = None


def get_crypto_service() -> CryptoService:
    """获取全局加密服务实例

    Returns:
        CryptoService实例

    Raises:
        ValueError: 如果未设置ENCRYPTION_KEY环境变量
    """
    global _crypto_service

    if _crypto_service is None:
        secret_key = os.getenv("ENCRYPTION_KEY")
        if not secret_key:
            # 开发环境使用默认密钥（生产环境必须设置）
            logger.warning(
                "encryption_key_not_set",
                message="使用默认加密密钥，生产环境必须设置ENCRYPTION_KEY环境变量",
            )
            secret_key = "dev-encryption-key-change-in-production"

        _crypto_service = CryptoService(secret_key)
        logger.info("crypto_service_initialized")

    return _crypto_service


def encrypt_api_key(api_key: str) -> str:
    """便捷函数：加密API密钥

    Args:
        api_key: API密钥明文

    Returns:
        加密后的API密钥
    """
    return get_crypto_service().encrypt(api_key)


def decrypt_api_key(encrypted_key: str) -> str:
    """便捷函数：解密API密钥

    Args:
        encrypted_key: 加密的API密钥

    Returns:
        解密后的API密钥明文
    """
    return get_crypto_service().decrypt(encrypted_key)
