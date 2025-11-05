"""
模型工厂和注册表

提供模型适配器的动态创建、注册、管理和热切换功能。
支持线程安全的模型切换和实例缓存。
"""

from typing import Dict, Type, Optional, List
import threading
import structlog
from datetime import datetime

from model_adapters.base import BaseModelAdapter
from model_adapters.config import ModelConfig
from model_adapters.exceptions import ModelConfigurationError

logger = structlog.get_logger(__name__)


class ModelRegistry:
    """模型适配器注册表

    管理所有已注册的模型适配器类，支持动态注册和查询。
    """

    def __init__(self):
        """初始化注册表"""
        self._registry: Dict[str, Type[BaseModelAdapter]] = {}
        self._lock = threading.Lock()

    def register(
        self, provider: str, adapter_class: Type[BaseModelAdapter]
    ) -> None:
        """注册模型适配器类

        Args:
            provider: 提供商标识（如qwen/deepseek/glm）
            adapter_class: 适配器类

        Raises:
            ValueError: 如果提供商已注册
        """
        with self._lock:
            if provider in self._registry:
                logger.warning(
                    "provider_already_registered",
                    provider=provider,
                    message="提供商已注册，将被覆盖",
                )
            self._registry[provider] = adapter_class
            logger.info("provider_registered", provider=provider)

    def unregister(self, provider: str) -> None:
        """注销模型适配器

        Args:
            provider: 提供商标识
        """
        with self._lock:
            if provider in self._registry:
                del self._registry[provider]
                logger.info("provider_unregistered", provider=provider)

    def get(self, provider: str) -> Optional[Type[BaseModelAdapter]]:
        """获取注册的适配器类

        Args:
            provider: 提供商标识

        Returns:
            适配器类，如果未注册则返回None
        """
        with self._lock:
            return self._registry.get(provider)

    def list_providers(self) -> List[str]:
        """列出所有已注册的提供商

        Returns:
            提供商标识列表
        """
        with self._lock:
            return list(self._registry.keys())

    def is_registered(self, provider: str) -> bool:
        """检查提供商是否已注册

        Args:
            provider: 提供商标识

        Returns:
            bool: True表示已注册
        """
        with self._lock:
            return provider in self._registry


class ModelFactory:
    """模型适配器工厂

    负责创建、管理和缓存模型适配器实例。
    支持线程安全的模型热切换。
    """

    def __init__(self, registry: Optional[ModelRegistry] = None):
        """初始化模型工厂

        Args:
            registry: 模型注册表，如果不提供则创建新的
        """
        self.registry = registry or ModelRegistry()
        self._active_models: Dict[str, BaseModelAdapter] = {}
        self._model_metadata: Dict[str, Dict] = {}
        self._lock = threading.RLock()  # 使用可重入锁
        self._default_model: Optional[str] = None

    def create_adapter(
        self,
        provider: str,
        api_key: str,
        base_url: str,
        model_name: str,
        **kwargs
    ) -> BaseModelAdapter:
        """创建模型适配器实例

        Args:
            provider: 提供商标识
            api_key: API密钥
            base_url: API基础URL
            model_name: 模型名称
            **kwargs: 其他参数

        Returns:
            BaseModelAdapter: 适配器实例

        Raises:
            ModelConfigurationError: 如果提供商未注册或创建失败
        """
        adapter_class = self.registry.get(provider)
        if not adapter_class:
            available = self.registry.list_providers()
            raise ModelConfigurationError(
                f"未注册的提供商: {provider}. 可用提供商: {available}"
            )

        try:
            adapter = adapter_class(
                api_key=api_key,
                base_url=base_url,
                model_name=model_name,
                **kwargs
            )
            logger.info(
                "adapter_created",
                provider=provider,
                model_name=model_name,
            )
            return adapter
        except Exception as e:
            logger.error(
                "adapter_creation_failed",
                provider=provider,
                error=str(e),
            )
            raise ModelConfigurationError(
                f"创建适配器失败: {provider} - {str(e)}"
            )

    def create_from_config(self, config: ModelConfig) -> BaseModelAdapter:
        """从配置对象创建适配器

        Args:
            config: 模型配置对象

        Returns:
            BaseModelAdapter: 适配器实例
        """
        return self.create_adapter(
            provider=config.provider,
            api_key=config.api_key,
            base_url=config.api_base_url,
            model_name=config.model_version,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            timeout=config.timeout,
            **(config.extra_params or {}),
        )

    async def register_model(
        self,
        name: str,
        adapter: BaseModelAdapter,
        set_as_default: bool = False,
    ) -> None:
        """注册并缓存模型实例

        Args:
            name: 模型标识名称（全局唯一）
            adapter: 适配器实例
            set_as_default: 是否设为默认模型

        Raises:
            ModelConfigurationError: 如果健康检查失败
        """
        # 先进行健康检查
        logger.info("checking_model_health", name=name)
        is_healthy = await adapter.health_check()

        if not is_healthy:
            raise ModelConfigurationError(
                f"模型健康检查失败: {name}"
            )

        with self._lock:
            self._active_models[name] = adapter
            self._model_metadata[name] = {
                "provider": adapter.__class__.__name__,
                "model_name": adapter.model_name,
                "base_url": adapter.base_url,
                "registered_at": datetime.now().isoformat(),
                "is_healthy": True,
            }

            if set_as_default or self._default_model is None:
                self._default_model = name

            logger.info(
                "model_registered",
                name=name,
                provider=adapter.__class__.__name__,
                is_default=name == self._default_model,
            )

    def unregister_model(self, name: str) -> None:
        """注销并移除缓存的模型实例

        Args:
            name: 模型标识名称
        """
        with self._lock:
            if name in self._active_models:
                del self._active_models[name]
                del self._model_metadata[name]

                # 如果删除的是默认模型，清空默认设置
                if self._default_model == name:
                    self._default_model = None

                logger.info("model_unregistered", name=name)

    def get_model(self, name: Optional[str] = None) -> BaseModelAdapter:
        """获取模型适配器实例

        Args:
            name: 模型标识名称，如果不提供则返回默认模型

        Returns:
            BaseModelAdapter: 适配器实例

        Raises:
            ModelConfigurationError: 如果模型不存在
        """
        with self._lock:
            if name is None:
                name = self._default_model

            if name is None:
                raise ModelConfigurationError("未设置默认模型")

            adapter = self._active_models.get(name)
            if adapter is None:
                available = list(self._active_models.keys())
                raise ModelConfigurationError(
                    f"模型不存在: {name}. 可用模型: {available}"
                )

            return adapter

    async def switch_model(
        self, name: str, set_as_default: bool = True
    ) -> BaseModelAdapter:
        """切换到指定模型

        Args:
            name: 目标模型名称
            set_as_default: 是否设为默认模型

        Returns:
            BaseModelAdapter: 目标模型适配器

        Raises:
            ModelConfigurationError: 如果模型不存在或不健康
        """
        with self._lock:
            adapter = self.get_model(name)

            # 健康检查
            logger.info("switching_model", target=name)
            is_healthy = await adapter.health_check()

            if not is_healthy:
                raise ModelConfigurationError(
                    f"目标模型不健康: {name}"
                )

            if set_as_default:
                self._default_model = name

            logger.info(
                "model_switched",
                new_default=name,
                is_default=set_as_default,
            )

            return adapter

    def list_models(self) -> List[Dict]:
        """列出所有已注册的模型

        Returns:
            模型信息列表
        """
        with self._lock:
            return [
                {
                    "name": name,
                    "is_default": name == self._default_model,
                    **metadata,
                }
                for name, metadata in self._model_metadata.items()
            ]

    def get_default_model_name(self) -> Optional[str]:
        """获取默认模型名称

        Returns:
            默认模型名称，如果未设置则返回None
        """
        with self._lock:
            return self._default_model

    def has_model(self, name: str) -> bool:
        """检查模型是否已注册

        Args:
            name: 模型名称

        Returns:
            bool: True表示已注册
        """
        with self._lock:
            return name in self._active_models

    async def health_check_all(self) -> Dict[str, bool]:
        """对所有模型进行健康检查

        Returns:
            Dict[str, bool]: 模型名称到健康状态的映射
        """
        results = {}
        with self._lock:
            models = list(self._active_models.items())

        for name, adapter in models:
            try:
                is_healthy = await adapter.health_check()
                results[name] = is_healthy

                # 更新元数据
                with self._lock:
                    if name in self._model_metadata:
                        self._model_metadata[name]["is_healthy"] = is_healthy
                        self._model_metadata[name]["last_check"] = (
                            datetime.now().isoformat()
                        )

                logger.info(
                    "model_health_checked",
                    name=name,
                    is_healthy=is_healthy,
                )
            except Exception as e:
                logger.error(
                    "health_check_failed",
                    name=name,
                    error=str(e),
                )
                results[name] = False

        return results


# 全局单例工厂实例
_global_factory: Optional[ModelFactory] = None
_factory_lock = threading.Lock()


def get_global_factory() -> ModelFactory:
    """获取全局模型工厂单例

    Returns:
        ModelFactory: 全局工厂实例
    """
    global _global_factory
    with _factory_lock:
        if _global_factory is None:
            _global_factory = ModelFactory()
            logger.info("global_factory_initialized")
        return _global_factory


def initialize_factory(
    registry: Optional[ModelRegistry] = None,
) -> ModelFactory:
    """初始化全局模型工厂

    Args:
        registry: 可选的自定义注册表

    Returns:
        ModelFactory: 全局工厂实例
    """
    global _global_factory
    with _factory_lock:
        _global_factory = ModelFactory(registry)
        logger.info("global_factory_reinitialized")
        return _global_factory
