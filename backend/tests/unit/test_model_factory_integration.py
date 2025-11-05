"""Test ModelFactory LangGraph integration methods."""

import pytest
from unittest.mock import MagicMock, AsyncMock

from model_adapters.model_factory import ModelFactory, get_global_factory
from model_adapters.base import BaseModelAdapter


@pytest.fixture
def mock_adapter():
    """Create a mock model adapter."""
    adapter = MagicMock(spec=BaseModelAdapter)
    adapter.model_name = "test-model"
    adapter.base_url = "https://api.test.com"
    adapter.health_check = AsyncMock(return_value=True)
    return adapter


@pytest.mark.asyncio
async def test_get_instance():
    """Test ModelFactory.get_instance() returns singleton."""
    factory1 = ModelFactory.get_instance()
    factory2 = ModelFactory.get_instance()

    assert factory1 is factory2
    assert isinstance(factory1, ModelFactory)


@pytest.mark.asyncio
async def test_get_langchain_model(mock_adapter):
    """Test get_langchain_model() returns LangChain wrapper."""
    from model_adapters.langchain_wrapper import LangChainModelAdapter

    factory = ModelFactory.get_instance()

    # Register a test model
    await factory.register_model("test-model", mock_adapter, set_as_default=True)

    # Get LangChain-wrapped model
    llm = factory.get_langchain_model()

    assert isinstance(llm, LangChainModelAdapter)
    assert llm.model_name == "test-model"


@pytest.mark.asyncio
async def test_get_langchain_model_by_name(mock_adapter):
    """Test get_langchain_model() with specific model name."""
    from model_adapters.langchain_wrapper import LangChainModelAdapter

    factory = ModelFactory.get_instance()

    # Register multiple models
    adapter1 = MagicMock(spec=BaseModelAdapter)
    adapter1.model_name = "model-1"
    adapter1.base_url = "https://api1.test.com"
    adapter1.health_check = AsyncMock(return_value=True)

    adapter2 = MagicMock(spec=BaseModelAdapter)
    adapter2.model_name = "model-2"
    adapter2.base_url = "https://api2.test.com"
    adapter2.health_check = AsyncMock(return_value=True)

    await factory.register_model("model-1", adapter1, set_as_default=True)
    await factory.register_model("model-2", adapter2, set_as_default=False)

    # Get specific model
    llm = factory.get_langchain_model("model-2")

    assert isinstance(llm, LangChainModelAdapter)
    assert llm.model_name == "model-2"


@pytest.mark.asyncio
async def test_get_langchain_model_no_default():
    """Test get_langchain_model() raises error when no default model."""
    from model_adapters.model_factory import initialize_factory
    from model_adapters.exceptions import ModelConfigurationError

    # Create a fresh factory without any models
    factory = initialize_factory()

    with pytest.raises(ModelConfigurationError, match="未设置默认模型"):
        factory.get_langchain_model()


def test_get_global_factory_is_singleton():
    """Test get_global_factory() returns same instance."""
    factory1 = get_global_factory()
    factory2 = get_global_factory()

    assert factory1 is factory2
