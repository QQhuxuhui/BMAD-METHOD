"""
Qwen千问3真实API集成测试

使用私有化部署的千问3模型进行测试。

运行方式:
  .venv/bin/python tests/integration/test_qwen_real.py
"""

import asyncio
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from model_adapters.qwen_adapter import QwenAdapter


async def test_real_qwen():
    """测试真实的千问3私有化部署API"""

    # 使用提供的私有化部署配置
    adapter = QwenAdapter(
        api_key="test-key",  # 私有化部署API KEY可以随意
        base_url="http://10.90.15.22:8103/v1",
        model_name="qwen3-30b-a3b",
        max_tokens=500,
        temperature=0.7,
    )

    print("=" * 60)
    print("测试千问3私有化部署")
    print("=" * 60)

    # 测试1: 健康检查
    print("\n[测试1] 健康检查...")
    try:
        is_healthy = await adapter.health_check()
        print(f"✅ 健康检查结果: {is_healthy}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        import traceback
        traceback.print_exc()
        return

    # 测试2: 简单对话
    print("\n[测试2] 简单对话测试...")
    try:
        messages = [
            {"role": "user", "content": "你好，请用一句话介绍你自己"}
        ]
        response = await adapter.chat(messages)

        print(f"✅ 模型响应:")
        print(f"  内容: {response.content}")
        print(f"  Token使用: {response.tokens_used}")
        print(f"  成本: ${response.cost}")
        print(f"  模型: {response.model}")
        print(f"  完成原因: {response.finish_reason}")
    except Exception as e:
        print(f"❌ 对话测试失败: {e}")
        import traceback
        traceback.print_exc()

    # 测试3: 流式输出
    print("\n[测试3] 流式输出测试...")
    try:
        messages = [
            {"role": "user", "content": "请数到5，每个数字单独输出"}
        ]
        print("模型输出: ", end="", flush=True)
        async for chunk in adapter.chat_stream(messages):
            print(chunk, end="", flush=True)
        print("\n✅ 流式输出完成")
    except Exception as e:
        print(f"\n❌ 流式输出测试失败: {e}")
        import traceback
        traceback.print_exc()

    # 测试4: 多轮对话
    print("\n[测试4] 多轮对话测试...")
    try:
        messages = [
            {"role": "system", "content": "你是一个Python编程助手"},
            {"role": "user", "content": "如何在Python中创建字典？"},
            {"role": "assistant", "content": "在Python中创建字典使用花括号{}。"},
            {"role": "user", "content": "给我一个例子"}
        ]
        response = await adapter.chat(messages)

        print(f"✅ 多轮对话响应:")
        print(f"  {response.content[:200]}...")  # 只显示前200字符
        print(f"  Token使用: {response.tokens_used}")
    except Exception as e:
        print(f"❌ 多轮对话测试失败: {e}")
        import traceback
        traceback.print_exc()

    # 测试5: 中文能力测试
    print("\n[测试5] 中文能力测试...")
    try:
        messages = [
            {"role": "user", "content": "请用三句话介绍一下中国的长城"}
        ]
        response = await adapter.chat(messages)

        print(f"✅ 中文响应:")
        print(f"  {response.content}")
        print(f"  Token使用: {response.tokens_used}")
    except Exception as e:
        print(f"❌ 中文能力测试失败: {e}")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_real_qwen())
