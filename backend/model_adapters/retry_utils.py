"""
重试机制工具函数

提供统一的HTTP请求重试和错误处理机制。
"""

from typing import Dict, Any, Optional
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log,
)
import structlog

from model_adapters.exceptions import (
    ModelUnavailableError,
    ModelTimeoutError,
    ModelQuotaExceededError,
    ModelResponseError,
)

logger = structlog.get_logger(__name__)


# 定义需要重试的异常类型
RETRYABLE_EXCEPTIONS = (
    httpx.TimeoutException,
    httpx.NetworkError,
    httpx.ConnectError,
    httpx.RemoteProtocolError,
)


def create_retry_decorator(
    max_attempts: int = 3,
    min_wait: float = 2.0,
    max_wait: float = 10.0,
    multiplier: float = 1.0,
):
    """创建重试装饰器

    Args:
        max_attempts: 最大重试次数
        min_wait: 最小等待时间（秒）
        max_wait: 最大等待时间（秒）
        multiplier: 指数退避乘数

    Returns:
        重试装饰器
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=multiplier, min=min_wait, max=max_wait),
        retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
        before_sleep=before_sleep_log(logger, "WARNING"),
        after=after_log(logger, "INFO"),
        reraise=True,
    )


@create_retry_decorator()
async def call_model_api(
    url: str,
    headers: Dict[str, str],
    data: Dict[str, Any],
    timeout: float = 30.0,
    stream: bool = False,
) -> httpx.Response:
    """调用模型API（带重试机制）

    Args:
        url: API端点URL
        headers: HTTP请求头
        data: 请求体数据
        timeout: 超时时间（秒）
        stream: 是否流式请求

    Returns:
        httpx.Response: HTTP响应对象

    Raises:
        ModelUnavailableError: 服务不可用（5xx错误）
        ModelQuotaExceededError: 配额超限（429错误）
        ModelTimeoutError: 请求超时
        ModelResponseError: 其他客户端错误（4xx）
    """
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            logger.info("calling_model_api", url=url, stream=stream)

            response = await client.post(
                url,
                headers=headers,
                json=data,
                timeout=timeout,
            )

            # 处理HTTP状态码
            if response.status_code == 200:
                return response
            elif response.status_code == 429:
                raise ModelQuotaExceededError(
                    f"API quota exceeded: {response.text}"
                )
            elif 500 <= response.status_code < 600:
                raise ModelUnavailableError(
                    f"Model service unavailable (HTTP {response.status_code}): {response.text}"
                )
            elif 400 <= response.status_code < 500:
                raise ModelResponseError(
                    f"Client error (HTTP {response.status_code}): {response.text}"
                )
            else:
                raise ModelResponseError(
                    f"Unexpected status code {response.status_code}: {response.text}"
                )

    except httpx.TimeoutException as e:
        logger.error("model_api_timeout", url=url, timeout=timeout)
        raise ModelTimeoutError(f"Request timeout after {timeout}s: {str(e)}")
    except (httpx.NetworkError, httpx.ConnectError) as e:
        logger.error("model_api_network_error", url=url, error=str(e))
        raise ModelUnavailableError(f"Network error: {str(e)}")
    except Exception as e:
        if isinstance(
            e,
            (
                ModelUnavailableError,
                ModelQuotaExceededError,
                ModelTimeoutError,
                ModelResponseError,
            ),
        ):
            raise
        logger.error("model_api_unexpected_error", url=url, error=str(e))
        raise ModelResponseError(f"Unexpected error: {str(e)}")


async def stream_model_api(
    url: str,
    headers: Dict[str, str],
    data: Dict[str, Any],
    timeout: float = 30.0,
) -> httpx.Response:
    """流式调用模型API（带重试机制）

    Note: 流式请求本身不会自动重试，但会使用相同的错误处理逻辑。

    Args:
        url: API端点URL
        headers: HTTP请求头
        data: 请求体数据（需包含stream=true）
        timeout: 超时时间（秒）

    Returns:
        httpx.Response: HTTP响应对象（需要调用者处理stream）

    Raises:
        ModelUnavailableError: 服务不可用
        ModelQuotaExceededError: 配额超限
        ModelTimeoutError: 请求超时
    """
    try:
        client = httpx.AsyncClient(timeout=timeout)
        logger.info("streaming_model_api", url=url)

        response = await client.post(
            url,
            headers=headers,
            json=data,
        )

        # 检查状态码
        if response.status_code == 200:
            return response
        elif response.status_code == 429:
            await client.aclose()
            raise ModelQuotaExceededError(
                f"API quota exceeded: {response.text}"
            )
        elif 500 <= response.status_code < 600:
            await client.aclose()
            raise ModelUnavailableError(
                f"Model service unavailable (HTTP {response.status_code})"
            )
        else:
            await client.aclose()
            raise ModelResponseError(
                f"HTTP {response.status_code}: {response.text}"
            )

    except httpx.TimeoutException as e:
        logger.error("stream_api_timeout", url=url)
        raise ModelTimeoutError(f"Stream request timeout: {str(e)}")
    except httpx.NetworkError as e:
        logger.error("stream_api_network_error", url=url)
        raise ModelUnavailableError(f"Network error: {str(e)}")


async def health_check_api(url: str, timeout: float = 5.0) -> bool:
    """健康检查API端点

    Args:
        url: API端点URL
        timeout: 超时时间（秒）

    Returns:
        bool: True表示健康，False表示不健康
    """
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            return response.status_code == 200
    except Exception as e:
        logger.warning("health_check_failed", url=url, error=str(e))
        return False
