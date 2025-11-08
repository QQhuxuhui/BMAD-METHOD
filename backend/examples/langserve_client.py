"""LangServe client example for BMAD workflow.

This example demonstrates how to use the LangServe RemoteRunnable
to interact with the BMAD workflow API endpoints.

Requirements:
    pip install langserve[client] httpx

Usage:
    python examples/langserve_client.py
"""

import asyncio
import os
from typing import Dict, Any

from langserve import RemoteRunnable


# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
BMAD_WORKFLOW_URL = f"{API_BASE_URL}/api/v1/bmad-workflow"
JWT_TOKEN = os.getenv("JWT_TOKEN", "your_jwt_token_here")


def get_headers() -> Dict[str, str]:
    """Get HTTP headers with JWT authentication.

    Returns:
        Dict containing Authorization header with Bearer token
    """
    return {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json",
    }


def example_invoke():
    """Example: Synchronous workflow invocation.

    This example shows how to invoke the workflow synchronously,
    blocking until the workflow completes and returns the result.
    """
    print("=" * 60)
    print("Example 1: Synchronous Invoke")
    print("=" * 60)

    # Create RemoteRunnable instance
    runnable = RemoteRunnable(
        url=BMAD_WORKFLOW_URL,
        headers=get_headers(),
    )

    # Prepare input
    input_data = {
        "problem_description": "优化100辆车的配送路线，最小化总行驶距离",
        "domain": "logistics",
        "constraints": ["实时交通限制", "电动车电池容量限制"],
    }

    print(f"\nInput: {input_data}\n")

    try:
        # Invoke workflow synchronously
        print("Invoking workflow... (this will block until complete)")
        result = runnable.invoke(input_data)

        print(f"\nResult:")
        print(f"  Workflow ID: {result.get('workflow_id')}")
        print(f"  Status: {result.get('status')}")
        print(f"  Current Phase: {result.get('current_phase')}")
        print(f"  Total Tokens: {result.get('total_tokens')}")
        print(f"  Total Cost: ${result.get('total_cost'):.2f}")

        if result.get('output_data'):
            print(f"\nOutput Data:")
            print(f"  Algorithm: {result.get('output_data', {}).get('algorithm')}")
            print(f"  Quality Score: {result.get('output_data', {}).get('quality_score')}")

    except Exception as e:
        print(f"\nError: {e}")


async def example_astream():
    """Example: Asynchronous streaming workflow execution.

    This example shows how to stream workflow execution events
    asynchronously, receiving updates in real-time.
    """
    print("\n" + "=" * 60)
    print("Example 2: Asynchronous Stream")
    print("=" * 60)

    # Create RemoteRunnable instance
    runnable = RemoteRunnable(
        url=BMAD_WORKFLOW_URL,
        headers=get_headers(),
    )

    # Prepare input
    input_data = {
        "problem_description": "设计一个电商推荐系统，提升用户转化率",
        "domain": "recommendation",
        "constraints": ["实时性要求", "冷启动问题"],
    }

    print(f"\nInput: {input_data}\n")

    try:
        print("Streaming workflow events...\n")

        # Stream workflow events
        async for event in runnable.astream(input_data):
            event_type = event.get("event", "unknown")
            data = event.get("data", {})
            timestamp = event.get("timestamp")

            print(f"[{timestamp}] Event: {event_type}")

            if event_type == "workflow_start":
                print(f"  Workflow ID: {data.get('workflow_id')}")
                print(f"  Status: {data.get('status')}")

            elif event_type == "phase_change":
                print(f"  Phase: {data.get('old_phase')} → {data.get('new_phase')}")

            elif event_type == "agent_output":
                print(f"  Agent: {event.get('agent_name')}")
                print(f"  Status: {data.get('status')}")
                print(f"  Tokens: {data.get('token_count')}")

            elif event_type == "interrupt":
                print(f"  Approval Point: {data.get('approval_point')}")
                print(f"  Approval ID: {data.get('approval_id')}")

            elif event_type == "error":
                print(f"  Error: {data.get('error')}")

            print()

        print("Stream completed.")

    except Exception as e:
        print(f"\nError: {e}")


def example_batch():
    """Example: Batch workflow invocation.

    This example shows how to invoke multiple workflows in batch,
    processing multiple problems simultaneously.
    """
    print("\n" + "=" * 60)
    print("Example 3: Batch Invoke")
    print("=" * 60)

    # Create RemoteRunnable instance
    runnable = RemoteRunnable(
        url=BMAD_WORKFLOW_URL,
        headers=get_headers(),
    )

    # Prepare batch inputs
    batch_inputs = [
        {
            "problem_description": "优化仓库库存管理策略",
            "domain": "inventory",
            "constraints": ["季节性需求波动"],
        },
        {
            "problem_description": "设计员工排班系统，平衡工作负载",
            "domain": "scheduling",
            "constraints": ["劳动法规限制", "技能匹配"],
        },
        {
            "problem_description": "优化网络广告投放ROI",
            "domain": "marketing",
            "constraints": ["预算限制", "目标受众"],
        },
    ]

    print(f"\nBatch size: {len(batch_inputs)}\n")

    try:
        print("Invoking batch workflows...")
        results = runnable.batch(batch_inputs)

        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"  Workflow ID: {result.get('workflow_id')}")
            print(f"  Status: {result.get('status')}")
            print(f"  Total Cost: ${result.get('total_cost'):.2f}")

    except Exception as e:
        print(f"\nError: {e}")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("BMAD Workflow LangServe Client Examples")
    print("=" * 60)
    print(f"\nAPI URL: {BMAD_WORKFLOW_URL}")
    print(f"JWT Token: {JWT_TOKEN[:20]}..." if len(JWT_TOKEN) > 20 else f"JWT Token: {JWT_TOKEN}")
    print("\nNOTE: Make sure to set JWT_TOKEN environment variable with a valid token.\n")

    # Example 1: Synchronous invoke
    example_invoke()

    # Example 2: Asynchronous stream
    asyncio.run(example_astream())

    # Example 3: Batch invoke
    example_batch()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
