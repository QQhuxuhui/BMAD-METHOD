"""
DeepSeek真实API集成测试

使用真实的DeepSeek-R1私有化部署进行测试。

运行方式:
  .venv/bin/python tests/integration/test_deepseek_real.py
"""

import asyncio
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from model_adapters.deepseek_adapter import DeepSeekAdapter


async def test_real_deepseek():
    """测试真实的DeepSeek-R1 API"""

    # 使用提供的私有化部署配置
    adapter = DeepSeekAdapter(
        api_key="sk-0b31af30018747f88bdec33341aea71f",
        base_url="http://api.chogori.hanyunplat.com/v1",
        model_name="service-deepseek-r1-0528",
        max_tokens=500,
        temperature=0.7,
    )

    print("=" * 60)
    print("测试DeepSeek-R1私有化部署")
    print("=" * 60)

    # 测试1: 健康检查
    print("\n[测试1] 健康检查...")
    try:
        is_healthy = await adapter.health_check()
        print(f"✅ 健康检查结果: {is_healthy}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return

    # 测试2: 简单对话
    print("\n[测试2] 简单对话测试...")
    try:
        messages = [
            {"role": "user", "content": "你好，请用一句话介绍自己"}
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
            {"role": "user", "content": "如何在Python中创建列表？"},
            {"role": "assistant", "content": "在Python中创建列表很简单，使用方括号[]即可。"},
            {"role": "user", "content": "给我一个例子"}
        ]
        response = await adapter.chat(messages)

        print(f"✅ 多轮对话响应:")
        print(f"  {response.content[:200]}...")  # 只显示前200字符
        print(f"  Token使用: {response.tokens_used}")
    except Exception as e:
        print(f"❌ 多轮对话测试失败: {e}")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_real_deepseek())
