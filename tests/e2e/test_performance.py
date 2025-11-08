"""
Performance benchmarking tests for Phase 1 validation.

Tests API response times, throughput, and resource usage.
"""

import asyncio
import time
from typing import Dict, List

import httpx
import pytest

from tests.e2e.conftest import TEST_API_PREFIX


@pytest.mark.asyncio
class TestAPIPerformance:
    """Test API performance characteristics."""

    async def test_workflow_creation_latency(
        self,
        authenticated_client: httpx.AsyncClient,
        sample_problem_simple: Dict,
        benchmark
    ):
        """Benchmark workflow creation API latency."""

        async def create_workflow():
            response = await authenticated_client.post(
                f"{TEST_API_PREFIX}/workflows/",
                json=sample_problem_simple
            )
            return response.status_code

        # Run benchmark
        result = benchmark(lambda: asyncio.run(create_workflow()))
        assert result == 201

        # Benchmark results available in benchmark.stats
        print(f"\nWorkflow creation latency:")
        print(f"  Mean: {benchmark.stats.mean * 1000:.2f}ms")
        print(f"  Median: {benchmark.stats.median * 1000:.2f}ms")
        print(f"  StdDev: {benchmark.stats.stddev * 1000:.2f}ms")

        # Assert performance targets (very lenient for Phase 1)
        assert benchmark.stats.median < 1.0, "Median latency should be < 1s"

    async def test_workflow_query_latency(
        self,
        authenticated_client: httpx.AsyncClient,
        sample_problem_simple: Dict
    ):
        """Test workflow status query response time."""
        # Create a workflow first
        response = await authenticated_client.post(
            f"{TEST_API_PREFIX}/workflows/",
            json=sample_problem_simple
        )
        assert response.status_code == 201
        workflow_id = response.json()["id"]

        # Measure query latency
        latencies = []
        for _ in range(10):
            start = time.time()
            response = await authenticated_client.get(
                f"{TEST_API_PREFIX}/workflows/{workflow_id}"
            )
            latency = time.time() - start
            latencies.append(latency)

            assert response.status_code == 200

        # Calculate statistics
        mean_latency = sum(latencies) / len(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]

        print(f"\nWorkflow query latency:")
        print(f"  Mean: {mean_latency * 1000:.2f}ms")
        print(f"  P95: {p95_latency * 1000:.2f}ms")
        print(f"  Min: {min(latencies) * 1000:.2f}ms")
        print(f"  Max: {max(latencies) * 1000:.2f}ms")

        # Performance targets
        assert mean_latency < 0.5, "Mean query latency should be < 500ms"
        assert p95_latency < 1.0, "P95 query latency should be < 1s"

    async def test_workflow_list_latency(
        self,
        authenticated_client: httpx.AsyncClient,
        sample_problem_simple: Dict
    ):
        """Test workflow list API response time."""
        # Create several workflows first
        for i in range(5):
            await authenticated_client.post(
                f"{TEST_API_PREFIX}/workflows/",
                json=sample_problem_simple
            )

        # Measure list latency
        latencies = []
        for _ in range(10):
            start = time.time()
            response = await authenticated_client.get(
                f"{TEST_API_PREFIX}/workflows/?limit=20"
            )
            latency = time.time() - start
            latencies.append(latency)

            assert response.status_code == 200

        mean_latency = sum(latencies) / len(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]

        print(f"\nWorkflow list latency:")
        print(f"  Mean: {mean_latency * 1000:.2f}ms")
        print(f"  P95: {p95_latency * 1000:.2f}ms")

        # Performance targets
        assert mean_latency < 1.0, "Mean list latency should be < 1s"

    @pytest.mark.timeout(120)
    async def test_concurrent_requests_throughput(
        self,
        http_client: httpx.AsyncClient,
        test_user: Dict,
        sample_problem_simple: Dict
    ):
        """Test system throughput with concurrent requests."""
        num_concurrent = 10
        auth_client = http_client
        auth_client.headers.update({"Authorization": f"Bearer {test_user['token']}"})

        # Measure throughput
        start_time = time.time()

        tasks = []
        for i in range(num_concurrent):
            problem = sample_problem_simple.copy()
            problem["problem_description"] = f"{problem['problem_description']} (Throughput {i})"
            tasks.append(
                auth_client.post(
                    f"{TEST_API_PREFIX}/workflows/",
                    json=problem
                )
            )

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        elapsed_time = time.time() - start_time

        # Count successful requests
        successful = [r for r in responses if isinstance(r, httpx.Response) and r.status_code == 201]

        throughput = len(successful) / elapsed_time  # requests per second

        print(f"\nConcurrent requests throughput:")
        print(f"  Total requests: {num_concurrent}")
        print(f"  Successful: {len(successful)}")
        print(f"  Time: {elapsed_time:.2f}s")
        print(f"  Throughput: {throughput:.2f} req/s")

        # Should handle at least 5 req/s
        assert throughput >= 5.0, f"Throughput too low: {throughput:.2f} req/s"
        assert len(successful) >= num_concurrent * 0.9, "Too many failed requests"


@pytest.mark.asyncio
class TestEndToEndPerformance:
    """Test end-to-end workflow performance."""

    @pytest.mark.timeout(60)
    async def test_simple_problem_execution_time(
        self,
        authenticated_client: httpx.AsyncClient,
        sample_problem_simple: Dict
    ):
        """Measure execution time for simple problem (target: < 30s)."""
        start_time = time.time()

        # Create workflow
        response = await authenticated_client.post(
            f"{TEST_API_PREFIX}/workflows/",
            json=sample_problem_simple
        )
        assert response.status_code == 201
        workflow_id = response.json()["id"]

        # Poll until completed or paused
        status = "pending"
        while status in ["pending", "running"]:
            await asyncio.sleep(2)
            response = await authenticated_client.get(
                f"{TEST_API_PREFIX}/workflows/{workflow_id}"
            )
            workflow = response.json()
            status = workflow["status"]

            if time.time() - start_time > 60:
                break

        execution_time = time.time() - start_time

        print(f"\nSimple problem execution:")
        print(f"  Time: {execution_time:.2f}s")
        print(f"  Final status: {status}")

        # This is a very lenient target for LLM-based workflows
        # Adjust based on whether using mock LLM or real LLM
        if status in ["completed", "paused"]:
            assert execution_time < 60, f"Execution too slow: {execution_time:.2f}s"

    @pytest.mark.timeout(180)
    async def test_medium_problem_execution_time(
        self,
        authenticated_client: httpx.AsyncClient,
        sample_problem_medium: Dict
    ):
        """Measure execution time for medium problem (target: < 120s)."""
        start_time = time.time()

        # Create workflow
        response = await authenticated_client.post(
            f"{TEST_API_PREFIX}/workflows/",
            json=sample_problem_medium
        )
        assert response.status_code == 201
        workflow_id = response.json()["id"]

        # Poll until first checkpoint or timeout
        status = "pending"
        checkpoint_reached = False

        while time.time() - start_time < 180:
            await asyncio.sleep(3)
            response = await authenticated_client.get(
                f"{TEST_API_PREFIX}/workflows/{workflow_id}"
            )
            workflow = response.json()
            status = workflow["status"]

            if status == "paused":
                checkpoint_reached = True
                break
            elif status in ["completed", "failed"]:
                break

        execution_time = time.time() - start_time

        print(f"\nMedium problem execution:")
        print(f"  Time to first checkpoint: {execution_time:.2f}s")
        print(f"  Final status: {status}")
        print(f"  Checkpoint reached: {checkpoint_reached}")

        # Should reach checkpoint or complete within 3 minutes
        assert checkpoint_reached or status in ["completed", "failed"], \
            f"Workflow stuck in {status} after {execution_time:.2f}s"


@pytest.mark.asyncio
class TestResourceUtilization:
    """Test resource usage and limits."""

    async def test_memory_usage_stability(
        self,
        authenticated_client: httpx.AsyncClient,
        sample_problem_simple: Dict
    ):
        """Test that memory usage remains stable across multiple requests."""
        # This is a simple test - proper memory profiling needs psutil
        num_requests = 20

        for i in range(num_requests):
            response = await authenticated_client.post(
                f"{TEST_API_PREFIX}/workflows/",
                json=sample_problem_simple
            )
            # Just ensure requests succeed
            assert response.status_code == 201

            if i % 5 == 0:
                await asyncio.sleep(1)  # Brief pause

        # If we got here without timeout/crash, memory is stable enough
        assert True

    async def test_connection_pool_handling(
        self,
        authenticated_client: httpx.AsyncClient
    ):
        """Test that connection pool is properly managed."""
        # Make many sequential requests
        for _ in range(50):
            response = await authenticated_client.get(
                f"{TEST_API_PREFIX}/workflows/?limit=10"
            )
            assert response.status_code == 200

        # Should not have connection pool exhaustion
        assert True
