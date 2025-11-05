"""
模型配置加载器

从环境变量和数据库加载模型配置，并初始化模型适配器。
"""

from typing import Dict, List, Optional
import structlog
from sqlmodel import Session, select

from app.core.config import settings
from app.core.crypto import decrypt_api_key
from app.models.model_config import ModelConfig
from model_adapters.base import BaseModelAdapter
from model_adapters.qwen_adapter import QwenAdapter
from model_adapters.deepseek_adapter import DeepSeekAdapter
from model_adapters.model_factory import ModelFactory

logger = structlog.get_logger(__name__)


class ModelConfigLoader:
    """模型配置加载器

    负责从环境变量和数据库加载模型配置，并创建相应的适配器实例。
    """

    def __init__(self):
        """初始化配置加载器"""
        self.factory = ModelFactory()

    def load_from_env(self) -> Dict[str, BaseModelAdapter]:
        """从环境变量加载模型配置

        Returns:
            Dict[str, BaseModelAdapter]: 模型名称到适配器实例的映射
        """
        adapters: Dict[str, BaseModelAdapter] = {}

        # 加载Qwen模型配置
        if settings.QWEN_API_KEY:
            try:
                qwen_adapter = QwenAdapter(
                    api_key=settings.QWEN_API_KEY,
                    base_url=settings.QWEN_API_BASE_URL,
                    model_name=settings.QWEN_MODEL_VERSION,
                    max_tokens=settings.QWEN_MAX_TOKENS,
                    temperature=settings.QWEN_TEMPERATURE,
                    timeout=settings.MODEL_DEFAULT_TIMEOUT,
                )
                adapters["qwen"] = qwen_adapter
                logger.info(
                    "loaded_qwen_from_env",
                    model=settings.QWEN_MODEL_VERSION,
                    base_url=settings.QWEN_API_BASE_URL,
                )
            except Exception as e:
                logger.error("failed_to_load_qwen_from_env", error=str(e))

        # 加载DeepSeek模型配置
        if settings.DEEPSEEK_API_KEY:
            try:
                deepseek_adapter = DeepSeekAdapter(
                    api_key=settings.DEEPSEEK_API_KEY,
                    base_url=settings.DEEPSEEK_API_BASE_URL,
                    model_name=settings.DEEPSEEK_MODEL_VERSION,
                    max_tokens=settings.DEEPSEEK_MAX_TOKENS,
                    temperature=settings.DEEPSEEK_TEMPERATURE,
                    timeout=settings.MODEL_DEFAULT_TIMEOUT,
                )
                adapters["deepseek"] = deepseek_adapter
                logger.info(
                    "loaded_deepseek_from_env",
                    model=settings.DEEPSEEK_MODEL_VERSION,
                    base_url=settings.DEEPSEEK_API_BASE_URL,
                )
            except Exception as e:
                logger.error("failed_to_load_deepseek_from_env", error=str(e))

        # TODO: 加载GLM模型配置（如果需要）
        # if settings.GLM_API_KEY:
        #     try:
        #         glm_adapter = GLMAdapter(...)
        #         adapters["glm"] = glm_adapter
        #     except Exception as e:
        #         logger.error("failed_to_load_glm_from_env", error=str(e))

        return adapters

    async def load_from_database(self, session: Session) -> Dict[str, BaseModelAdapter]:
        """从数据库加载模型配置

        Args:
            session: 数据库会话

        Returns:
            Dict[str, BaseModelAdapter]: 模型名称到适配器实例的映射
        """
        adapters: Dict[str, BaseModelAdapter] = {}

        try:
            # 查询所有启用的模型配置
            statement = select(ModelConfig).where(ModelConfig.is_active == True)
            configs = session.exec(statement).all()

            for config in configs:
                try:
                    # 解密API密钥
                    api_key = (
                        decrypt_api_key(config.api_key_encrypted)
                        if config.api_key_encrypted
                        else ""
                    )

                    # 根据provider创建对应的适配器
                    adapter = self._create_adapter_from_config(config, api_key)

                    if adapter:
                        adapters[config.name] = adapter
                        logger.info(
                            "loaded_model_from_database",
                            name=config.name,
                            provider=config.provider,
                            model=config.model_version,
                        )
                except Exception as e:
                    logger.error(
                        "failed_to_load_model_from_database",
                        name=config.name,
                        error=str(e),
                    )

        except Exception as e:
            logger.error("failed_to_query_database", error=str(e))

        return adapters

    def _create_adapter_from_config(
        self, config: ModelConfig, api_key: str
    ) -> Optional[BaseModelAdapter]:
        """根据配置创建适配器实例

        Args:
            config: 模型配置
            api_key: 解密后的API密钥

        Returns:
            BaseModelAdapter: 适配器实例，如果provider不支持则返回None
        """
        provider_map = {
            "qwen": QwenAdapter,
            "deepseek": DeepSeekAdapter,
            # "glm": GLMAdapter,  # TODO: 添加GLM适配器
            # "vllm": VLLMAdapter,  # TODO: 添加vLLM适配器
            # "ollama": OllamaAdapter,  # TODO: 添加Ollama适配器
        }

        adapter_class = provider_map.get(config.provider)
        if not adapter_class:
            logger.warning(
                "unsupported_provider",
                provider=config.provider,
                name=config.name,
            )
            return None

        try:
            return adapter_class(
                api_key=api_key,
                base_url=config.api_base_url,
                model_name=config.model_version,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                timeout=config.timeout,
            )
        except Exception as e:
            logger.error(
                "failed_to_create_adapter",
                provider=config.provider,
                name=config.name,
                error=str(e),
            )
            return None

    async def initialize_factory(
        self, session: Optional[Session] = None
    ) -> ModelFactory:
        """初始化模型工厂

        首先从环境变量加载配置，然后从数据库加载（如果提供了session）。
        数据库配置会覆盖同名的环境变量配置。

        Args:
            session: 可选的数据库会话

        Returns:
            ModelFactory: 初始化后的模型工厂实例
        """
        # 1. 从环境变量加载
        env_adapters = self.load_from_env()
        for name, adapter in env_adapters.items():
            try:
                await self.factory.register_model(
                    name=name,
                    adapter=adapter,
                    set_as_default=(name == settings.DEFAULT_MODEL_PROVIDER),
                )
            except Exception as e:
                logger.error(
                    "failed_to_register_model_from_env",
                    name=name,
                    error=str(e),
                )

        # 2. 从数据库加载（如果提供了session）
        if session:
            db_adapters = await self.load_from_database(session)
            for name, adapter in db_adapters.items():
                try:
                    await self.factory.register_model(
                        name=name,
                        adapter=adapter,
                        set_as_default=(name == settings.DEFAULT_MODEL_NAME),
                    )
                except Exception as e:
                    logger.error(
                        "failed_to_register_model_from_database",
                        name=name,
                        error=str(e),
                    )

        # 3. 记录加载结果
        registered_models_list = self.factory.list_models()
        registered_model_names = [m["name"] for m in registered_models_list]
        logger.info(
            "factory_initialized",
            total_models=len(registered_model_names),
            models=registered_model_names,
            default_model=self.factory._default_model,
        )

        return self.factory


# 全局配置加载器实例
_config_loader: Optional[ModelConfigLoader] = None


def get_config_loader() -> ModelConfigLoader:
    """获取全局配置加载器实例

    Returns:
        ModelConfigLoader: 配置加载器实例
    """
    global _config_loader
    if _config_loader is None:
        _config_loader = ModelConfigLoader()
    return _config_loader


async def initialize_models(session: Optional[Session] = None) -> ModelFactory:
    """便捷函数：初始化模型工厂

    Args:
        session: 可选的数据库会话

    Returns:
        ModelFactory: 初始化后的模型工厂实例
    """
    loader = get_config_loader()
    return await loader.initialize_factory(session)
