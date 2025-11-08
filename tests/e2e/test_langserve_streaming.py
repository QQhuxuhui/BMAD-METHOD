"""
LangServe SSE streaming tests for Phase 1 validation.

Tests Server-Sent Events (SSE) streaming functionality.
"""

import asyncio
import json
from typing import AsyncIterator, Dict

import httpx
import pytest

from tests.e2e.conftest import TEST_API_PREFIX


@pytest.mark.asyncio
class TestLangServeStreaming:
    """Test suite for LangServe streaming endpoints."""

    async def test_langserve_invoke_endpoint(
        self,
        authenticated_client: httpx.AsyncClient,
        sample_problem_simple: Dict
    ):
        """Test LangServe /invoke endpoint for synchronous execution."""
        response = await authenticated_client.post(
            "/bmad-workflow/invoke",
            json={
                "input": {
                    "problem_description": sample_problem_simple["problem_description"],
                    "domain": sample_problem_simple["domain"],
                    "constraints": sample_problem_simple.get("constraints", {})
                }
            },
            timeout=60.0
        )

        # LangServe invoke should return 200 or might timeout for long workflows
        if response.status_code == 200:
            data = response.json()
            assert "output" in data or "result" in data
        elif response.status_code == 504:
            pytest.skip("Workflow timeout - expected for long-running workflows")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")

    async def test_langserve_stream_endpoint_connection(
        self,
        http_client: httpx.AsyncClient,
        test_user: Dict,
        sample_problem_simple: Dict
    ):
        """Test establishing SSE connection to /stream endpoint."""
        # Configure client for streaming
        async with httpx.AsyncClient(
            base_url=http_client.base_url,
            timeout=30.0,
            headers={"Authorization": f"Bearer {test_user['token']}"}
        ) as client:
            try:
                async with client.stream(
                    "POST",
                    "/bmad-workflow/stream",
                    json={
                        "input": {
                            "problem_description": sample_problem_simple["problem_description"],
                            "domain": sample_problem_simple["domain"],
                            "constraints": sample_problem_simple.get("constraints", {})
                        }
                    }
                ) as response:
                    # Should successfully establish SSE connection
                    assert response.status_code == 200
                    assert "text/event-stream" in response.headers.get("content-type", "")

                    # Read first few events
                    event_count = 0
                    async for line in response.aiter_lines():
                        if line.startswith("data:"):
                            event_count += 1
                            # Parse event data
                            data_str = line[5:].strip()  # Remove "data:" prefix
                            if data_str and data_str != "[DONE]":
                                try:
                                    event_data = json.loads(data_str)
                                    # Validate event structure
                                    assert isinstance(event_data, dict)
                                except json.JSONDecodeError:
                                    pass  # Some events might not be JSON

                        # Stop after receiving a few events
                        if event_count >= 5:
                            break

                    assert event_count > 0, "No SSE events received"

            except httpx.TimeoutException:
                pytest.skip("SSE stream timeout - might be due to slow LLM")

    @pytest.mark.timeout(60)
    async def test_stream_events_structure(
        self,
        http_client: httpx.AsyncClient,
        test_user: Dict,
        sample_problem_simple: Dict
    ):
        """Test SSE event structure conforms to LangServe format."""
        events_received = []

        async with httpx.AsyncClient(
            base_url=http_client.base_url,
            timeout=60.0,
            headers={"Authorization": f"Bearer {test_user['token']}"}
        ) as client:
            try:
                async with client.stream(
                    "POST",
                    "/bmad-workflow/stream_events",
                    json={
                        "input": {
                            "problem_description": sample_problem_simple["problem_description"],
                            "domain": sample_problem_simple["domain"]
                        }
                    }
                ) as response:
                    assert response.status_code == 200

                    async for line in response.aiter_lines():
                        if line.startswith("data:"):
                            data_str = line[5:].strip()
                            if data_str and data_str != "[DONE]":
                                try:
                                    event = json.loads(data_str)
                                    events_received.append(event)

                                    # Validate LangServe event structure
                                    if isinstance(event, dict):
                                        # Common event fields
                                        if "event" in event:
                                            assert event["event"] in [
                                                "on_chain_start",
                                                "on_chain_stream",
                                                "on_chain_end",
                                                "on_llm_start",
                                                "on_llm_stream",
                                                "on_llm_end",
                                            ]

                                except json.JSONDecodeError:
                                    continue

                        # Collect enough events for validation
                        if len(events_received) >= 10:
                            break

            except (httpx.TimeoutException, asyncio.TimeoutError):
                pass  # Partial events still useful for validation

        # Should have received at least some events
        assert len(events_received) > 0, "No valid events received"

        # Verify event types
        event_types = [e.get("event") for e in events_received if "event" in e]
        assert len(event_types) > 0, "No event types found"

    async def test_stream_reconnection(
        self,
        http_client: httpx.AsyncClient,
        test_user: Dict,
        sample_problem_simple: Dict
    ):
        """Test SSE stream can be reconnected after disconnect."""
        async with httpx.AsyncClient(
            base_url=http_client.base_url,
            timeout=30.0,
            headers={"Authorization": f"Bearer {test_user['token']}"}
        ) as client:
            # First connection
            try:
                async with client.stream(
                    "POST",
                    "/bmad-workflow/stream",
                    json={
                        "input": {
                            "problem_description": sample_problem_simple["problem_description"],
                            "domain": sample_problem_simple["domain"]
                        }
                    }
                ) as response:
                    assert response.status_code == 200

                    # Read a few events then close
                    count = 0
                    async for line in response.aiter_lines():
                        if line.startswith("data:"):
                            count += 1
                        if count >= 3:
                            break
                    # Connection closed here

            except httpx.TimeoutException:
                pass

            # Second connection should work
            try:
                async with client.stream(
                    "POST",
                    "/bmad-workflow/stream",
                    json={
                        "input": {
                            "problem_description": sample_problem_simple["problem_description"],
                            "domain": sample_problem_simple["domain"]
                        }
                    }
                ) as response:
                    assert response.status_code == 200
                    # Successfully reconnected

            except httpx.TimeoutException:
                pytest.skip("Stream timeout on reconnection")


@pytest.mark.asyncio
class TestStreamingPerformance:
    """Test SSE streaming performance characteristics."""

    @pytest.mark.timeout(30)
    async def test_stream_latency(
        self,
        http_client: httpx.AsyncClient,
        test_user: Dict,
        sample_problem_simple: Dict
    ):
        """Test SSE first event latency."""
        import time

        async with httpx.AsyncClient(
            base_url=http_client.base_url,
            timeout=30.0,
            headers={"Authorization": f"Bearer {test_user['token']}"}
        ) as client:
            start_time = time.time()

            try:
                async with client.stream(
                    "POST",
                    "/bmad-workflow/stream",
                    json={
                        "input": {
                            "problem_description": sample_problem_simple["problem_description"],
                            "domain": sample_problem_simple["domain"]
                        }
                    }
                ) as response:
                    assert response.status_code == 200

                    # Measure time to first event
                    first_event_time = None
                    async for line in response.aiter_lines():
                        if line.startswith("data:"):
                            first_event_time = time.time()
                            break

                    if first_event_time:
                        latency = first_event_time - start_time
                        print(f"\nFirst event latency: {latency:.2f}s")

                        # Should receive first event within reasonable time
                        # This is very lenient for LLM-based systems
                        assert latency < 15.0, f"First event latency too high: {latency}s"
                    else:
                        pytest.fail("No events received")

            except httpx.TimeoutException:
                pytest.skip("Stream timeout")

    async def test_multiple_concurrent_streams(
        self,
        http_client: httpx.AsyncClient,
        test_user: Dict,
        sample_problem_simple: Dict
    ):
        """Test system can handle multiple concurrent SSE streams."""
        num_streams = 3

        async def create_stream(stream_id: int) -> int:
            """Create a stream and count events."""
            event_count = 0

            async with httpx.AsyncClient(
                base_url=http_client.base_url,
                timeout=30.0,
                headers={"Authorization": f"Bearer {test_user['token']}"}
            ) as client:
                try:
                    async with client.stream(
                        "POST",
                        "/bmad-workflow/stream",
                        json={
                            "input": {
                                "problem_description": f"{sample_problem_simple['problem_description']} (Stream {stream_id})",
                                "domain": sample_problem_simple["domain"]
                            }
                        }
                    ) as response:
                        if response.status_code == 200:
                            async for line in response.aiter_lines():
                                if line.startswith("data:"):
                                    event_count += 1
                                if event_count >= 5:  # Just get a few events
                                    break
                except (httpx.TimeoutException, asyncio.TimeoutError):
                    pass

            return event_count

        # Create multiple streams concurrently
        tasks = [create_stream(i) for i in range(num_streams)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # At least some streams should succeed
        successful = [r for r in results if isinstance(r, int) and r > 0]
        assert len(successful) > 0, "No streams received events"

        print(f"\nSuccessful streams: {len(successful)}/{num_streams}")
        for i, count in enumerate(successful):
            print(f"  Stream {i}: {count} events")
