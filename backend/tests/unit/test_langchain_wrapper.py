"""
测试LangChain包装器
"""

import pytest
from typing import List, Dict, AsyncIterator
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from model_adapters.langchain_wrapper import (
    LangChainModelAdapter,
    create_langchain_adapter,
)
from model_adapters.base import BaseModelAdapter, ModelResponse
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


# 测试用虚拟适配器
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


class TestLangChainModelAdapter:
    """测试LangChain模型适配器"""

    @pytest.mark.asyncio
    async def test_message_conversion(self):
        """测试消息格式转换"""
        adapter = DummyAdapter(
            api_key="test",
            base_url="http://test.com",
            model_name="test-model",
        )
        langchain_model = LangChainModelAdapter(
            adapter=adapter,
            model_name="test",
        )

        messages = [
            SystemMessage(content="You are a helpful assistant"),
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there"),
        ]

        converted = langchain_model._convert_messages_to_dict(messages)

        assert len(converted) == 3
        assert converted[0] == {"role": "system", "content": "You are a helpful assistant"}
        assert converted[1] == {"role": "user", "content": "Hello"}
        assert converted[2] == {"role": "assistant", "content": "Hi there"}

    @pytest.mark.asyncio
    async def test_agenerate(self):
        """测试异步生成"""
        adapter = DummyAdapter(
            api_key="test",
            base_url="http://test.com",
            model_name="test-model",
        )
        langchain_model = LangChainModelAdapter(
            adapter=adapter,
            model_name="test",
        )

        messages = [HumanMessage(content="Hello")]
        result = await langchain_model._agenerate(messages)

        assert result is not None
        assert len(result.generations) == 1
        assert result.generations[0].message.content == "Test response"
        assert result.generations[0].generation_info["tokens_used"] == 10
        assert result.generations[0].generation_info["cost"] == 0.001

    @pytest.mark.asyncio
    async def test_astream(self):
        """测试异步流式生成"""
        adapter = DummyAdapter(
            api_key="test",
            base_url="http://test.com",
            model_name="test-model",
        )
        langchain_model = LangChainModelAdapter(
            adapter=adapter,
            model_name="test",
        )

        messages = [HumanMessage(content="Hello")]
        chunks = []

        async for chunk in langchain_model._astream(messages):
            chunks.append(chunk.message.content)

        assert len(chunks) == 3
        assert "".join(chunks) == "Hello World"

    def test_generate_sync(self):
        """测试同步生成（使用事件循环）"""
        adapter = DummyAdapter(
            api_key="test",
            base_url="http://test.com",
            model_name="test-model",
        )
        langchain_model = LangChainModelAdapter(
            adapter=adapter,
            model_name="test",
        )

        messages = [HumanMessage(content="Hello")]
        result = langchain_model._generate(messages)

        assert result is not None
        assert len(result.generations) == 1
        assert result.generations[0].message.content == "Test response"

    def test_llm_type(self):
        """测试LLM类型标识"""
        adapter = DummyAdapter(
            api_key="test",
            base_url="http://test.com",
            model_name="test-model",
        )
        langchain_model = LangChainModelAdapter(
            adapter=adapter,
            model_name="test",
        )

        assert langchain_model._llm_type == "custom-DummyAdapter"

    def test_identifying_params(self):
        """测试标识参数"""
        adapter = DummyAdapter(
            api_key="test",
            base_url="http://test.com",
            model_name="test-model",
        )
        langchain_model = LangChainModelAdapter(
            adapter=adapter,
            model_name="test",
        )

        params = langchain_model._identifying_params
        assert params["model_name"] == "test"
        assert params["adapter_class"] == "DummyAdapter"
        assert params["base_url"] == "http://test.com"

    def test_create_langchain_adapter(self):
        """测试工厂函数"""
        adapter = DummyAdapter(
            api_key="test",
            base_url="http://test.com",
            model_name="test-model",
        )

        langchain_model = create_langchain_adapter(adapter, streaming=True)

        assert langchain_model.adapter == adapter
        assert langchain_model.model_name == "test-model"
        assert langchain_model.streaming is True
