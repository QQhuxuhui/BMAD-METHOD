"""Prometheus metrics configuration for the application.

This module sets up and configures Prometheus metrics for monitoring the application.
"""

from prometheus_client import Counter, Histogram, Gauge
from starlette_prometheus import metrics, PrometheusMiddleware

# Request metrics
http_requests_total = Counter("http_requests_total", "Total number of HTTP requests", ["method", "endpoint", "status"])

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds", "HTTP request duration in seconds", ["method", "endpoint"]
)

# Database metrics
db_connections = Gauge("db_connections", "Number of active database connections")

# Custom business metrics
orders_processed = Counter("orders_processed_total", "Total number of orders processed")

# ==================== 模型适配器监控指标 ====================

# 模型调用计数器
model_requests_total = Counter(
    "model_requests_total",
    "Total number of model API requests",
    ["model_name", "provider", "status"],  # status: success/error
)

# 模型调用延迟
model_request_duration_seconds = Histogram(
    "model_request_duration_seconds",
    "Model API request duration in seconds",
    ["model_name", "provider"],
    buckets=[0.1, 0.3, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
)

# 模型错误计数器
model_errors_total = Counter(
    "model_errors_total",
    "Total number of model API errors",
    ["model_name", "provider", "error_type"],
)

# Token消耗
model_tokens_used_total = Counter(
    "model_tokens_used_total",
    "Total number of tokens used",
    ["model_name", "provider", "token_type"],  # token_type: input/output
)

# API成本
model_cost_total = Counter(
    "model_cost_total",
    "Total API cost in USD",
    ["model_name", "provider"],
)

# 当前活跃模型数量
active_models_count = Gauge(
    "active_models_count",
    "Number of currently active models",
    ["provider"],
)

# 模型健康状态
model_health_status = Gauge(
    "model_health_status",
    "Model health status (1=healthy, 0=unhealthy)",
    ["model_name", "provider"],
)

# 健康检查延迟
model_health_check_duration_seconds = Histogram(
    "model_health_check_duration_seconds",
    "Model health check duration in seconds",
    ["model_name", "provider"],
    buckets=[0.1, 0.3, 0.5, 1.0, 2.0, 5.0],
)

# LLM推理延迟（保留原有指标以保持兼容）
llm_inference_duration_seconds = Histogram(
    "llm_inference_duration_seconds",
    "Time spent processing LLM inference",
    ["model"],
    buckets=[0.1, 0.3, 0.5, 1.0, 2.0, 5.0]
)

llm_stream_duration_seconds = Histogram(
    "llm_stream_duration_seconds",
    "Time spent processing LLM stream inference",
    ["model"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)


def setup_metrics(app):
    """Set up Prometheus metrics middleware and endpoints.

    Args:
        app: FastAPI application instance
    """
    # Add Prometheus middleware
    app.add_middleware(PrometheusMiddleware)

    # Add metrics endpoint
    app.add_route("/metrics", metrics)
