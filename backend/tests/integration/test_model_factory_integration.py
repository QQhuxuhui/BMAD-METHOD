"""
模型工厂集成测试

使用真实的DeepSeek-R1和Qwen3私有化部署进行测试。

运行方式:
  .venv/bin/python tests/integration/test_model_factory_integration.py
"""

import asyncio
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from model_adapters.model_factory import ModelRegistry, ModelFactory
from model_adapters.deepseek_adapter import DeepSeekAdapter
from model_adapters.qwen_adapter import QwenAdapter


async def test_model_factory_integration():
    """测试模型工厂的完整功能"""

    print("=" * 60)
    print("模型工厂集成测试")
    print("=" * 60)

    # 初始化注册表和工厂
    print("\n[测试1] 初始化模型工厂...")
    registry = ModelRegistry()
    registry.register("deepseek", DeepSeekAdapter)
    registry.register("qwen", QwenAdapter)

    factory = ModelFactory(registry)
    print(f"✅ 已注册提供商: {factory.registry.list_providers()}")

    # 创建DeepSeek适配器
    print("\n[测试2] 创建DeepSeek-R1适配器...")
    deepseek_adapter = factory.create_adapter(
        provider="deepseek",
        api_key="test-key",
        base_url="http://10.90.15.22:8103/v1",
        model_name="deepseek-r1-distill-qwen-32b",
        max_tokens=500,
        temperature=0.7,
    )
    print("✅ DeepSeek适配器创建成功")

    # 创建Qwen适配器
    print("\n[测试3] 创建Qwen3适配器...")
    qwen_adapter = factory.create_adapter(
        provider="qwen",
        api_key="test-key",
        base_url="http://10.90.15.22:8103/v1",
        model_name="qwen3-30b-a3b",
        max_tokens=500,
        temperature=0.7,
    )
    print("✅ Qwen适配器创建成功")

    # 注册DeepSeek模型（会自动设为默认）
    print("\n[测试4] 注册DeepSeek模型...")
    try:
        await factory.register_model("deepseek-r1", deepseek_adapter)
        print("✅ DeepSeek模型注册成功")
        print(f"  默认模型: {factory.get_default_model_name()}")
    except Exception as e:
        print(f"❌ 注册失败: {e}")
        return

    # 注册Qwen模型（不设为默认）
    print("\n[测试5] 注册Qwen模型...")
    try:
        await factory.register_model("qwen3", qwen_adapter, set_as_default=False)
        print("✅ Qwen模型注册成功")
        print(f"  默认模型: {factory.get_default_model_name()}")
    except Exception as e:
        print(f"❌ 注册失败: {e}")
        return

    # 列出所有模型
    print("\n[测试6] 列出所有已注册的模型...")
    models = factory.list_models()
    for model in models:
        print(f"  - {model['name']} (默认: {model['is_default']})")
        print(f"    提供商: {model['provider']}, 模型: {model['model_name']}")

    # 使用默认模型进行对话
    print("\n[测试7] 使用默认模型（DeepSeek）进行对话...")
    try:
        default_model = factory.get_model()
        messages = [{"role": "user", "content": "用一句话介绍你自己"}]
        response = await default_model.chat(messages)
        print(f"✅ 响应: {response.content[:100]}...")
        print(f"  Token: {response.tokens_used}, 成本: ${response.cost}")
    except Exception as e:
        print(f"❌ 对话失败: {e}")

    # 切换到Qwen模型
    print("\n[测试8] 切换到Qwen模型...")
    try:
        await factory.switch_model("qwen3")
        print(f"✅ 切换成功，当前默认模型: {factory.get_default_model_name()}")
    except Exception as e:
        print(f"❌ 切换失败: {e}")
        return

    # 使用切换后的模型进行对话
    print("\n[测试9] 使用切换后的模型（Qwen）进行对话...")
    try:
        qwen_model = factory.get_model()
        messages = [{"role": "user", "content": "介绍一下你自己"}]
        response = await qwen_model.chat(messages)
        print(f"✅ 响应: {response.content[:100]}...")
        print(f"  Token: {response.tokens_used}, 成本: ${response.cost}")
    except Exception as e:
        print(f"❌ 对话失败: {e}")

    # 指定模型进行对话
    print("\n[测试10] 指定使用DeepSeek模型进行对话...")
    try:
        deepseek_model = factory.get_model("deepseek-r1")
        messages = [{"role": "user", "content": "你好"}]
        response = await deepseek_model.chat(messages)
        print(f"✅ 响应: {response.content[:100]}...")
    except Exception as e:
        print(f"❌ 对话失败: {e}")

    # 批量健康检查
    print("\n[测试11] 批量健康检查...")
    try:
        health_results = await factory.health_check_all()
        for name, is_healthy in health_results.items():
            status = "✅ 健康" if is_healthy else "❌ 不健康"
            print(f"  {name}: {status}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")

    # 注销模型
    print("\n[测试12] 注销DeepSeek模型...")
    factory.unregister_model("deepseek-r1")
    print(f"✅ 注销成功")
    print(f"  剩余模型: {[m['name'] for m in factory.list_models()]}")
    print(f"  当前默认模型: {factory.get_default_model_name()}")

    print("\n" + "=" * 60)
    print("✅ 模型工厂集成测试完成！")
    print("=" * 60)


async def test_concurrent_usage():
    """测试并发使用场景"""

    print("\n" + "=" * 60)
    print("并发使用测试")
    print("=" * 60)

    # 初始化
    registry = ModelRegistry()
    registry.register("deepseek", DeepSeekAdapter)
    registry.register("qwen", QwenAdapter)
    factory = ModelFactory(registry)

    # 注册两个模型
    deepseek_adapter = factory.create_adapter(
        provider="deepseek",
        api_key="test-key",
        base_url="http://10.90.15.22:8103/v1",
        model_name="deepseek-r1-distill-qwen-32b",
    )
    qwen_adapter = factory.create_adapter(
        provider="qwen",
        api_key="test-key",
        base_url="http://10.90.15.22:8103/v1",
        model_name="qwen3-30b-a3b",
    )

    await factory.register_model("deepseek-r1", deepseek_adapter)
    await factory.register_model("qwen3", qwen_adapter)

    print("\n[测试13] 并发调用两个模型...")

    async def call_model(model_name: str, question: str):
        model = factory.get_model(model_name)
        messages = [{"role": "user", "content": question}]
        response = await model.chat(messages)
        return f"{model_name}: {response.content[:50]}..."

    try:
        # 并发调用
        tasks = [
            call_model("deepseek-r1", "1+1等于几？"),
            call_model("qwen3", "2+2等于几？"),
        ]
        results = await asyncio.gather(*tasks)

        print("✅ 并发调用成功：")
        for result in results:
            print(f"  {result}")
    except Exception as e:
        print(f"❌ 并发调用失败: {e}")

    print("\n" + "=" * 60)
    print("✅ 并发使用测试完成！")
    print("=" * 60)


async def main():
    """运行所有测试"""
    try:
        await test_model_factory_integration()
        await test_concurrent_usage()
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试出现异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
