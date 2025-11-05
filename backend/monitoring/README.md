# 模型适配器监控

本目录包含模型适配器的Prometheus和Grafana监控配置。

## 监控指标

### 1. 模型请求指标

- **model_requests_total**: 模型API请求总数
  - 标签: `model_name`, `provider`, `status` (success/error)

- **model_request_duration_seconds**: 模型API请求延迟分布
  - 标签: `model_name`, `provider`
  - 分桶: 0.1s, 0.3s, 0.5s, 1s, 2s, 5s, 10s, 30s

- **model_errors_total**: 模型API错误总数
  - 标签: `model_name`, `provider`, `error_type`

### 2. Token和成本指标

- **model_tokens_used_total**: Token使用总数
  - 标签: `model_name`, `provider`, `token_type` (input/output)

- **model_cost_total**: API调用成本累计（USD）
  - 标签: `model_name`, `provider`

### 3. 模型健康指标

- **active_models_count**: 当前活跃模型数量
  - 标签: `provider`

- **model_health_status**: 模型健康状态 (1=健康, 0=不健康)
  - 标签: `model_name`, `provider`

- **model_health_check_duration_seconds**: 健康检查延迟
  - 标签: `model_name`, `provider`

## 使用方法

### 1. 在代码中记录指标

#### 方式1: 使用上下文管理器（推荐）

```python
from model_adapters.metrics_utils import ModelMetricsRecorder

recorder = ModelMetricsRecorder(
    model_name="qwen3-30b-a3b",
    provider="qwen"
)

# 记录请求
with recorder.record_request():
    response = await adapter.chat(messages)

# 记录token和成本
recorder.record_tokens(
    input_tokens=response.metadata["input_tokens"],
    output_tokens=response.metadata["output_tokens"]
)
recorder.record_cost(response.cost)

# 记录健康检查
with recorder.record_health_check():
    is_healthy = await adapter.health_check()
    recorder.record_health_status(is_healthy)
```

#### 方式2: 使用便捷函数

```python
from model_adapters.metrics_utils import record_model_response

# 自动记录响应中的所有指标
record_model_response(
    model_name="deepseek-r1",
    provider="deepseek",
    response=response
)
```

### 2. 启动Prometheus

```bash
# 使用Docker运行Prometheus
docker run -d \
  -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

示例 `prometheus.yml` 配置：

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'bmad-backend'
    static_configs:
      - targets: ['host.docker.internal:8000']
```

### 3. 导入Grafana仪表盘

1. 访问Grafana (默认: http://localhost:3000)
2. 导航到 Dashboard > Import
3. 上传 `grafana/model-adapter-dashboard.json`
4. 选择Prometheus数据源
5. 点击 Import

### 4. 访问指标端点

应用启动后，可以通过以下端点访问原始指标：

```bash
curl http://localhost:8000/metrics
```

## 常用查询示例

### Prometheus查询

1. **过去5分钟的平均请求速率**:

   ```promql
   rate(model_requests_total[5m])
   ```

2. **P95响应延迟**:

   ```promql
   histogram_quantile(0.95, rate(model_request_duration_seconds_bucket[5m]))
   ```

3. **错误率**:

   ```promql
   rate(model_requests_total{status="error"}[5m]) / rate(model_requests_total[5m])
   ```

4. **按模型的Token消耗速率**:

   ```promql
   sum by (model_name) (rate(model_tokens_used_total[5m]))
   ```

5. **总API成本（每小时）**:
   ```promql
   increase(model_cost_total[1h])
   ```

### Grafana告警规则示例

1. **高错误率告警** (>5%):

   ```promql
   sum(rate(model_requests_total{status="error"}[5m])) / sum(rate(model_requests_total[5m])) > 0.05
   ```

2. **高延迟告警** (P95 > 5s):

   ```promql
   histogram_quantile(0.95, rate(model_request_duration_seconds_bucket[5m])) > 5
   ```

3. **模型不健康告警**:
   ```promql
   model_health_status == 0
   ```

## 仪表盘面板说明

1. **模型请求速率**: 实时请求速率，区分成功和失败
2. **响应延迟**: P50, P95, P99延迟指标
3. **总错误率**: 所有模型的整体错误率
4. **活跃模型数量**: 当前注册的模型总数
5. **Token消耗速率**: 输入/输出token的使用速率
6. **API成本累计**: 各模型的成本累计
7. **模型健康状态**: 各模型的实时健康状态表格
8. **错误类型分布**: 按错误类型分类的错误统计
9. **模型使用分布**: 各模型的请求分布
10. **健康检查延迟**: 健康检查的响应时间

## 最佳实践

1. **指标采集频率**: 建议scrape_interval设置为15-30秒
2. **数据保留期**: 根据需求设置，建议至少保留7-30天
3. **告警配置**: 为关键指标设置告警（错误率、延迟、健康状态）
4. **成本监控**: 定期检查成本累计，优化Token使用
5. **性能优化**: 基于P95/P99延迟指标进行性能调优

## 故障排查

### 指标未显示

1. 检查应用是否正常运行
2. 确认 `/metrics` 端点可访问
3. 检查Prometheus配置中的target地址
4. 查看Prometheus UI中的target状态

### Grafana显示"No Data"

1. 确认Prometheus数据源配置正确
2. 检查查询语句是否有数据返回
3. 确认时间范围设置正确
4. 检查模型是否有实际请求流量

## 参考资料

- [Prometheus文档](https://prometheus.io/docs/)
- [Grafana文档](https://grafana.com/docs/)
- [prometheus_client Python库](https://github.com/prometheus/client_python)
