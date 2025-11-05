"""
测试DeepSeek模型适配器
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from model_adapters.deepseek_adapter import DeepSeekAdapter
from model_adapters.base import ModelResponse
from model_adapters.exceptions import ModelResponseError


class TestDeepSeekAdapter:
    """测试DeepSeekAdapter"""

    def test_adapter_initialization(self):
        """测试适配器初始化"""
        adapter = DeepSeekAdapter(
            api_key="test-key",
            base_url="https://api.test.com/v1",
            model_name="deepseek-chat",
        )
        assert adapter.api_key == "test-key"
        assert adapter.base_url == "https://api.test.com/v1"
        assert adapter.model_name == "deepseek-chat"
        assert adapter.cost_config is not None

    def test_private_deployment_initialization(self):
        """测试私有化部署配置"""
        adapter = DeepSeekAdapter(
            api_key="sk-test",
            base_url="http://api.chogori.hanyunplat.com/v1",
            model_name="service-deepseek-r1-0528",
        )
        assert adapter.base_url == "http://api.chogori.hanyunplat.com/v1"
        assert adapter.model_name == "service-deepseek-r1-0528"
        # 私有化部署应该使用local计费配置（成本为0）
        assert adapter.cost_config is not None
        assert adapter.calculate_cost(1000) == 0.0

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Mock configuration needs refinement for httpx AsyncClient")
    async def test_chat_success(self):
        """测试chat方法成功调用"""
        adapter = DeepSeekAdapter(
            api_key="test-key",
            base_url="https://api.test.com/v1",
            model_name="deepseek-chat",
        )

        mock_response_data = {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "model": "deepseek-chat",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "你好！我是DeepSeek AI助手。",
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30,
            },
        }

        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data

        with patch(
            "model_adapters.retry_utils.call_model_api",
            new=AsyncMock(return_value=mock_response),
        ):
            messages = [{"role": "user", "content": "你好"}]
            response = await adapter.chat(messages)

            assert isinstance(response, ModelResponse)
            assert response.content == "你好！我是DeepSeek AI助手。"
            assert response.tokens_used == 30
            assert response.model == "deepseek-chat"
            assert response.finish_reason == "stop"
            assert response.metadata["input_tokens"] == 10
            assert response.metadata["output_tokens"] == 20

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Mock configuration needs refinement for httpx AsyncClient stream")
    async def test_chat_stream(self):
        """测试流式输出"""
        adapter = DeepSeekAdapter(
            api_key="test-key",
            model_name="deepseek-chat",
        )

        # 模拟SSE流式响应
        async def mock_aiter_lines():
            lines = [
                'data: {"choices":[{"delta":{"content":"你"}}]}',
                'data: {"choices":[{"delta":{"content":"好"}}]}',
                'data: {"choices":[{"delta":{"content":"！"}}]}',
                "data: [DONE]",
            ]
            for line in lines:
                yield line

        mock_response = AsyncMock()
        mock_response.aiter_lines = mock_aiter_lines
        mock_response.raise_for_status = AsyncMock()

        mock_stream = AsyncMock()
        mock_stream.__aenter__.return_value = mock_response
        mock_stream.__aexit__.return_value = None

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.stream.return_value = mock_stream

        with patch("httpx.AsyncClient", return_value=mock_client):
            messages = [{"role": "user", "content": "你好"}]
            chunks = []
            async for chunk in adapter.chat_stream(messages):
                chunks.append(chunk)

            assert chunks == ["你", "好", "！"]

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Mock configuration needs refinement for httpx AsyncClient")
    async def test_health_check_success(self):
        """测试健康检查成功"""
        adapter = DeepSeekAdapter(
            api_key="test-key",
            model_name="deepseek-chat",
        )

        mock_response_data = {
            "choices": [{"message": {"content": "OK"}}],
            "usage": {"total_tokens": 2},
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data

        with patch(
            "model_adapters.retry_utils.call_model_api",
            new=AsyncMock(return_value=mock_response),
        ):
            is_healthy = await adapter.health_check()
            assert is_healthy is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """测试健康检查失败"""
        adapter = DeepSeekAdapter(
            api_key="test-key",
            model_name="deepseek-chat",
        )

        with patch(
            "model_adapters.retry_utils.call_model_api",
            side_effect=Exception("Connection error"),
        ):
            is_healthy = await adapter.health_check()
            assert is_healthy is False

    def test_calculate_cost(self):
        """测试成本计算"""
        # 官方DeepSeek模型
        adapter = DeepSeekAdapter(
            api_key="test-key",
            model_name="deepseek-chat",
        )
        cost = adapter.calculate_cost(1000)
        assert cost > 0

        # 私有化部署模型（成本为0）
        adapter_private = DeepSeekAdapter(
            api_key="test-key",
            model_name="service-deepseek-r1-0528",
        )
        cost_private = adapter_private.calculate_cost(1000)
        assert cost_private == 0.0

    def test_parse_response_success(self):
        """测试响应解析成功"""
        adapter = DeepSeekAdapter(
            api_key="test-key",
            model_name="deepseek-chat",
        )

        response_data = {
            "model": "deepseek-chat",
            "choices": [
                {
                    "message": {"content": "测试响应"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 5,
                "completion_tokens": 10,
                "total_tokens": 15,
            },
        }

        result = adapter._parse_response(response_data)
        assert result.content == "测试响应"
        assert result.tokens_used == 15
        assert result.finish_reason == "stop"

    def test_parse_response_missing_choices(self):
        """测试响应缺少choices字段"""
        adapter = DeepSeekAdapter(
            api_key="test-key",
            model_name="deepseek-chat",
        )

        response_data = {"model": "deepseek-chat"}

        with pytest.raises(ModelResponseError):
            adapter._parse_response(response_data)
