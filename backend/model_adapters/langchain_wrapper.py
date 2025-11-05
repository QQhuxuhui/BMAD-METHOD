"""
LangChain兼容包装器

将自定义模型适配器包装为LangChain兼容的ChatModel，
以便与LangGraph工作流无缝集成。
"""

from typing import List, Optional, Any, AsyncIterator, Dict
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult, ChatGenerationChunk
from langchain_core.callbacks import (
    CallbackManagerForLLMRun,
    AsyncCallbackManagerForLLMRun,
)
import structlog

from backend.model_adapters.base import BaseModelAdapter, ModelResponse

logger = structlog.get_logger(__name__)


class LangChainModelAdapter(BaseChatModel):
    """LangChain兼容的模型适配器包装器

    将自定义的BaseModelAdapter包装为LangChain的BaseChatModel，
    使其能够在LangGraph工作流中使用。
    """

    adapter: BaseModelAdapter
    """底层的模型适配器实例"""

    model_name: str = "custom-model"
    """模型名称"""

    streaming: bool = False
    """是否支持流式输出"""

    class Config:
        arbitrary_types_allowed = True

    def _convert_messages_to_dict(
        self, messages: List[BaseMessage]
    ) -> List[Dict[str, str]]:
        """将LangChain消息转换为字典格式

        Args:
            messages: LangChain消息对象列表

        Returns:
            List[Dict[str, str]]: 字典格式的消息列表
        """
        result = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                result.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                result.append({"role": "assistant", "content": msg.content})
            elif isinstance(msg, SystemMessage):
                result.append({"role": "system", "content": msg.content})
            else:
                # 其他类型消息默认作为user角色
                result.append({"role": "user", "content": msg.content})
        return result

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """同步生成响应（LangChain要求实现）

        Note: 由于我们的适配器是异步的，这里抛出异常提示使用异步方法。

        Args:
            messages: 输入消息列表
            stop: 停止词列表
            run_manager: 回调管理器
            **kwargs: 额外参数

        Raises:
            NotImplementedError: 提示使用异步方法
        """
        raise NotImplementedError(
            "Synchronous generation not supported. Use ainvoke() or agenerate() instead."
        )

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """异步生成响应

        Args:
            messages: 输入消息列表
            stop: 停止词列表（暂不支持）
            run_manager: 异步回调管理器
            **kwargs: 额外参数

        Returns:
            ChatResult: LangChain聊天结果对象
        """
        # 转换消息格式
        dict_messages = self._convert_messages_to_dict(messages)

        # 调用底层适配器
        logger.info(
            "langchain_adapter_generating",
            adapter=self.adapter.__class__.__name__,
            num_messages=len(messages),
        )

        response: ModelResponse = await self.adapter.chat(
            dict_messages, **kwargs
        )

        # 转换为LangChain格式
        ai_message = AIMessage(content=response.content)
        generation = ChatGeneration(
            message=ai_message,
            generation_info={
                "tokens_used": response.tokens_used,
                "cost": response.cost,
                "model": response.model,
                "finish_reason": response.finish_reason,
                "metadata": response.metadata,
            },
        )

        # 触发回调
        if run_manager:
            await run_manager.on_llm_end(
                ChatResult(generations=[generation]),
                run_id=run_manager.run_id,
            )

        return ChatResult(generations=[generation])

    async def _astream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        """异步流式生成响应

        Args:
            messages: 输入消息列表
            stop: 停止词列表
            run_manager: 异步回调管理器
            **kwargs: 额外参数

        Yields:
            ChatGenerationChunk: LangChain流式生成块
        """
        # 转换消息格式
        dict_messages = self._convert_messages_to_dict(messages)

        logger.info(
            "langchain_adapter_streaming",
            adapter=self.adapter.__class__.__name__,
        )

        # 流式调用底层适配器
        async for chunk in self.adapter.chat_stream(dict_messages, **kwargs):
            ai_chunk = AIMessage(content=chunk)
            yield ChatGenerationChunk(message=ai_chunk)

            # 触发回调
            if run_manager:
                await run_manager.on_llm_new_token(chunk)

    @property
    def _llm_type(self) -> str:
        """返回LLM类型标识"""
        return f"custom-{self.adapter.__class__.__name__}"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """返回标识参数"""
        return {
            "model_name": self.model_name,
            "adapter_class": self.adapter.__class__.__name__,
            "base_url": self.adapter.base_url,
        }


def create_langchain_adapter(
    base_adapter: BaseModelAdapter, streaming: bool = False
) -> LangChainModelAdapter:
    """工厂函数：创建LangChain兼容的适配器

    Args:
        base_adapter: 底层模型适配器实例
        streaming: 是否启用流式输出

    Returns:
        LangChainModelAdapter: LangChain兼容的适配器实例
    """
    return LangChainModelAdapter(
        adapter=base_adapter,
        model_name=base_adapter.model_name,
        streaming=streaming,
    )
