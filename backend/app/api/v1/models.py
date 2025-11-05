"""
模型管理 API 端点

提供模型配置管理、模型交互和模型管理功能的REST API。
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session
import structlog

from app.core.database import get_session
from app.models.model_config import (
    ModelConfig,
    ModelConfigCreate,
    ModelConfigUpdate,
    ModelConfigRead,
)
from app.core.crypto import encrypt_api_key, decrypt_api_key
from model_adapters.config_loader import get_config_loader
from model_adapters.model_factory import get_model_factory
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)

router = APIRouter()


# ================================================================================
# 请求/响应模型
# ================================================================================


class ChatRequest(BaseModel):
    """聊天请求"""

    messages: List[dict] = Field(description="消息列表")
    model_name: Optional[str] = Field(
        default=None, description="模型名称（可选，默认使用当前默认模型）"
    )
    temperature: Optional[float] = Field(
        default=None, ge=0.0, le=2.0, description="温度参数"
    )
    max_tokens: Optional[int] = Field(
        default=None, ge=1, le=32768, description="最大token数"
    )


class ChatResponse(BaseModel):
    """聊天响应"""

    content: str = Field(description="回复内容")
    model: str = Field(description="使用的模型")
    tokens_used: int = Field(description="消耗的token数")
    cost: float = Field(description="成本（USD）")
    finish_reason: str = Field(description="结束原因")


class ModelInfo(BaseModel):
    """模型信息"""

    name: str = Field(description="模型名称")
    is_default: bool = Field(description="是否为默认模型")
    metadata: dict = Field(description="模型元数据")


# ================================================================================
# 模型配置管理端点
# ================================================================================


@router.post(
    "/configs",
    response_model=ModelConfigRead,
    status_code=status.HTTP_201_CREATED,
    summary="创建模型配置",
)
async def create_model_config(
    config: ModelConfigCreate,
    session: Session = Depends(get_session),
):
    """
    创建新的模型配置

    Args:
        config: 模型配置信息
        session: 数据库会话

    Returns:
        ModelConfigRead: 创建的模型配置（不包含敏感信息）
    """
    try:
        # 检查名称是否已存在
        from sqlmodel import select

        statement = select(ModelConfig).where(ModelConfig.name == config.name)
        existing = session.exec(statement).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"模型配置名称 '{config.name}' 已存在",
            )

        # 加密API密钥
        encrypted_key = encrypt_api_key(config.api_key)

        # 创建数据库记录
        db_config = ModelConfig(
            **config.model_dump(exclude={"api_key"}),
            api_key_encrypted=encrypted_key,
        )

        session.add(db_config)
        session.commit()
        session.refresh(db_config)

        logger.info(
            "model_config_created",
            name=config.name,
            provider=config.provider,
        )

        return db_config

    except HTTPException:
        raise
    except Exception as e:
        logger.error("failed_to_create_model_config", error=str(e))
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建模型配置失败: {str(e)}",
        )


@router.get(
    "/configs",
    response_model=List[ModelConfigRead],
    summary="获取所有模型配置",
)
async def list_model_configs(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    session: Session = Depends(get_session),
):
    """
    获取所有模型配置列表

    Args:
        skip: 跳过的记录数
        limit: 返回的最大记录数
        active_only: 是否只返回启用的配置
        session: 数据库会话

    Returns:
        List[ModelConfigRead]: 模型配置列表
    """
    try:
        from sqlmodel import select

        statement = select(ModelConfig)

        if active_only:
            statement = statement.where(ModelConfig.is_active == True)

        statement = statement.offset(skip).limit(limit)
        configs = session.exec(statement).all()

        logger.info("model_configs_listed", count=len(configs))

        return configs

    except Exception as e:
        logger.error("failed_to_list_model_configs", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取模型配置列表失败: {str(e)}",
        )


@router.get(
    "/configs/{config_id}",
    response_model=ModelConfigRead,
    summary="获取模型配置详情",
)
async def get_model_config(
    config_id: UUID,
    session: Session = Depends(get_session),
):
    """
    获取指定ID的模型配置

    Args:
        config_id: 配置ID
        session: 数据库会话

    Returns:
        ModelConfigRead: 模型配置详情
    """
    try:
        config = session.get(ModelConfig, config_id)

        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"模型配置 {config_id} 不存在",
            )

        return config

    except HTTPException:
        raise
    except Exception as e:
        logger.error("failed_to_get_model_config", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取模型配置失败: {str(e)}",
        )


@router.patch(
    "/configs/{config_id}",
    response_model=ModelConfigRead,
    summary="更新模型配置",
)
async def update_model_config(
    config_id: UUID,
    config_update: ModelConfigUpdate,
    session: Session = Depends(get_session),
):
    """
    更新指定ID的模型配置

    Args:
        config_id: 配置ID
        config_update: 更新的配置信息
        session: 数据库会话

    Returns:
        ModelConfigRead: 更新后的模型配置
    """
    try:
        config = session.get(ModelConfig, config_id)

        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"模型配置 {config_id} 不存在",
            )

        # 更新字段
        update_data = config_update.model_dump(exclude_unset=True)

        # 如果更新了API密钥，需要重新加密
        if "api_key" in update_data:
            api_key = update_data.pop("api_key")
            if api_key:
                update_data["api_key_encrypted"] = encrypt_api_key(api_key)

        for field, value in update_data.items():
            setattr(config, field, value)

        session.add(config)
        session.commit()
        session.refresh(config)

        logger.info("model_config_updated", config_id=str(config_id))

        return config

    except HTTPException:
        raise
    except Exception as e:
        logger.error("failed_to_update_model_config", error=str(e))
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新模型配置失败: {str(e)}",
        )


@router.delete(
    "/configs/{config_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除模型配置",
)
async def delete_model_config(
    config_id: UUID,
    session: Session = Depends(get_session),
):
    """
    删除指定ID的模型配置

    Args:
        config_id: 配置ID
        session: 数据库会话
    """
    try:
        config = session.get(ModelConfig, config_id)

        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"模型配置 {config_id} 不存在",
            )

        session.delete(config)
        session.commit()

        logger.info("model_config_deleted", config_id=str(config_id))

    except HTTPException:
        raise
    except Exception as e:
        logger.error("failed_to_delete_model_config", error=str(e))
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除模型配置失败: {str(e)}",
        )


# ================================================================================
# 模型交互端点
# ================================================================================


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="模型对话",
)
async def chat(request: ChatRequest):
    """
    与模型进行对话

    Args:
        request: 聊天请求

    Returns:
        ChatResponse: 模型回复
    """
    try:
        factory = get_model_factory()

        # 获取适配器
        if request.model_name:
            adapter = await factory.get_model(request.model_name)
        else:
            adapter = await factory.get_default_model()

        if not adapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到可用的模型",
            )

        # 准备参数
        kwargs = {}
        if request.temperature is not None:
            kwargs["temperature"] = request.temperature
        if request.max_tokens is not None:
            kwargs["max_tokens"] = request.max_tokens

        # 调用模型
        response = await adapter.chat(request.messages, **kwargs)

        return ChatResponse(
            content=response.content,
            model=response.model,
            tokens_used=response.tokens_used,
            cost=response.cost,
            finish_reason=response.finish_reason,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("chat_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"对话失败: {str(e)}",
        )


@router.post(
    "/chat/stream",
    summary="流式对话",
)
async def chat_stream(request: ChatRequest):
    """
    与模型进行流式对话

    Args:
        request: 聊天请求

    Returns:
        StreamingResponse: 流式响应
    """
    try:
        factory = get_model_factory()

        # 获取适配器
        if request.model_name:
            adapter = await factory.get_model(request.model_name)
        else:
            adapter = await factory.get_default_model()

        if not adapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到可用的模型",
            )

        # 准备参数
        kwargs = {}
        if request.temperature is not None:
            kwargs["temperature"] = request.temperature
        if request.max_tokens is not None:
            kwargs["max_tokens"] = request.max_tokens

        # 创建流式生成器
        async def generate():
            async for chunk in adapter.chat_stream(request.messages, **kwargs):
                yield chunk

        return StreamingResponse(generate(), media_type="text/event-stream")

    except HTTPException:
        raise
    except Exception as e:
        logger.error("chat_stream_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"流式对话失败: {str(e)}",
        )


# ================================================================================
# 模型管理端点
# ================================================================================


@router.get(
    "/list",
    response_model=List[ModelInfo],
    summary="列出所有已注册的模型",
)
async def list_models():
    """
    列出所有已注册的模型

    Returns:
        List[ModelInfo]: 模型信息列表
    """
    try:
        factory = get_model_factory()
        models = factory.list_models()

        return [ModelInfo(**model) for model in models]

    except Exception as e:
        logger.error("list_models_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取模型列表失败: {str(e)}",
        )


@router.post(
    "/switch/{model_name}",
    response_model=ModelInfo,
    summary="切换默认模型",
)
async def switch_default_model(model_name: str):
    """
    切换默认模型

    Args:
        model_name: 模型名称

    Returns:
        ModelInfo: 切换后的模型信息
    """
    try:
        factory = get_model_factory()

        adapter = await factory.get_model(model_name)
        if not adapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"模型 '{model_name}' 不存在",
            )

        # 切换默认模型
        await factory.switch_default_model(model_name)

        logger.info("default_model_switched", model_name=model_name)

        # 返回模型信息
        models = factory.list_models()
        for model in models:
            if model["name"] == model_name:
                return ModelInfo(**model)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("switch_model_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"切换模型失败: {str(e)}",
        )


@router.get(
    "/health/{model_name}",
    summary="检查模型健康状态",
)
async def check_model_health(model_name: str):
    """
    检查指定模型的健康状态

    Args:
        model_name: 模型名称

    Returns:
        dict: 健康检查结果
    """
    try:
        factory = get_model_factory()

        adapter = await factory.get_model(model_name)
        if not adapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"模型 '{model_name}' 不存在",
            )

        # 执行健康检查
        is_healthy = await adapter.health_check()

        from datetime import datetime, UTC

        return {
            "model_name": model_name,
            "healthy": is_healthy,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("health_check_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"健康检查失败: {str(e)}",
        )
