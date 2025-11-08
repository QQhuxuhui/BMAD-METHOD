```# End-to-End Tests for Phase 1 Validation

This directory contains the complete test suite for validating Phase 1 of the BMAD project.

## Test Structure

```

tests/e2e/
├── conftest.py # Pytest fixtures and helpers
├── test-design.md # Test design document
├── test_api_integration.py # API endpoint integration tests
├── test_langserve_streaming.py # SSE streaming tests
├── test_hitl_complete.py # HITL workflow tests
├── test_performance.py # Performance benchmarks
└── README.md # This file

````

## Prerequisites

1. **Backend services running**:
   ```bash
   cd backend
   docker-compose up -d  # Start PostgreSQL and Redis
   uv run uvicorn app.main:app --reload  # Start FastAPI
````

2. **Python dependencies**:

   ```bash
   cd backend
   uv pip install pytest pytest-asyncio httpx pytest-benchmark pytest-timeout
   ```

3. **Environment variables** (optional):
   ```bash
   export TEST_BASE_URL=http://localhost:8000
   export TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/bmad_test
   export TEST_MODEL_PROVIDER=mock  # Use mock LLM for faster tests
   ```

## Running Tests

### Run all E2E tests

```bash
pytest tests/e2e/ -v
```

### Run specific test suites

```bash
# API integration tests only
pytest tests/e2e/test_api_integration.py -v

# HITL workflow tests only
pytest tests/e2e/test_hitl_complete.py -v

# Performance tests only
pytest tests/e2e/test_performance.py -v

# Streaming tests only
pytest tests/e2e/test_langserve_streaming.py -v
```

### Run with markers

```bash
# Run only fast tests (exclude slow integration tests)
pytest tests/e2e/ -v -m "not slow"

# Run performance benchmarks
pytest tests/e2e/test_performance.py -v --benchmark-only
```

### Generate HTML report

```bash
pytest tests/e2e/ -v --html=reports/e2e-report.html --self-contained-html
```

### Run with coverage

```bash
pytest tests/e2e/ -v --cov=app --cov-report=html
```

## Test Scenarios

### 1. API Integration Tests (`test_api_integration.py`)

- ✅ User registration and login
- ✅ Workflow creation and status query
- ✅ Workflow list with pagination
- ✅ Access control between users
- ✅ Complete workflow execution
- ✅ Error handling and validation

**Expected Duration**: 2-5 minutes

### 2. LangServe Streaming Tests (`test_langserve_streaming.py`)

- ✅ SSE connection establishment
- ✅ Event stream structure validation
- ✅ Stream reconnection
- ✅ First event latency
- ✅ Concurrent streams

**Expected Duration**: 1-3 minutes

### 3. HITL Workflow Tests (`test_hitl_complete.py`)

- ✅ Approval workflow (approve at all checkpoints)
- ✅ Rejection workflow
- ✅ Modification workflow
- ✅ Multiple approval points
- ✅ Concurrent HITL approvals

**Expected Duration**: 3-8 minutes (depends on LLM)

### 4. Performance Tests (`test_performance.py`)

- ✅ API latency (p50, p95, p99)
- ✅ Throughput (concurrent requests)
- ✅ End-to-end execution time
- ✅ Resource utilization

**Expected Duration**: 2-5 minutes

## Performance Targets

| Metric             | Target    | Actual |
| ------------------ | --------- | ------ |
| API Response (p50) | < 200ms   | TBD    |
| API Response (p95) | < 1s      | TBD    |
| Throughput         | > 5 req/s | TBD    |
| Simple Problem E2E | < 30s     | TBD    |
| Medium Problem E2E | < 120s    | TBD    |

## Troubleshooting

### Tests timeout

- Increase timeout: `pytest tests/e2e/ -v --timeout=300`
- Use mock LLM: `export TEST_MODEL_PROVIDER=mock`
- Check backend logs: `docker logs bmad-backend-dev`

### Database errors

- Reset test database:
  ```bash
  psql -U postgres -c "DROP DATABASE bmad_test; CREATE DATABASE bmad_test;"
  ```

### Connection refused

- Verify backend is running: `curl http://localhost:8000/health`
- Check port: `lsof -i :8000`

### SSL/TLS errors

- Use HTTP for local testing: `export TEST_BASE_URL=http://localhost:8000`

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Run E2E Tests
  run: |
    export TEST_MODEL_PROVIDER=mock
    pytest tests/e2e/ -v --junit-xml=reports/e2e-results.xml
```

## Test Data

Test fixtures use predefined problem sets:

- **Simple**: Array max value (< 10s)
- **Medium**: VRP logistics optimization (< 60s)
- **Complex**: Job shop scheduling (< 5min)

## Known Limitations

1. **No frontend browser tests**: Playwright not configured yet
2. **Mock LLM recommended**: Real LLM tests can be slow and flaky
3. **Test isolation**: Each test creates its own user, but database is shared

## Next Steps

- [ ] Add Playwright for frontend E2E tests
- [ ] Implement load testing with Locust
- [ ] Add test data generators
- [ ] Set up CI/CD pipeline
- [ ] Add visual regression tests

## Contact

For questions about tests, see:

- Test design: `tests/e2e/test-design.md`
- Story 1.8: `docs/stories/1.8.story.md`

```

```
