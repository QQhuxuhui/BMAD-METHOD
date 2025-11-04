#!/usr/bin/env python3
"""
BMAD LangGraph 1.0 环境验证脚本

验证项：
1. Python版本（>=3.11）
2. 关键包安装验证
3. PostgreSQL连接测试
4. Redis连接测试
5. LangGraph基础功能测试
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def print_section(title: str):
    """打印章节标题"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def check_python_version() -> bool:
    """验证Python版本"""
    print_section("1. Python版本检查")

    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    print(f"当前Python版本: {version_str}")

    if version.major == 3 and version.minor >= 11:
        print("✅ Python版本符合要求（>= 3.11）")
        return True
    else:
        print(f"❌ Python版本不符合要求（需要 >= 3.11，当前 {version_str}）")
        return False


def check_packages() -> bool:
    """验证关键包安装"""
    print_section("2. 关键包安装检查")

    required_packages = {
        'langgraph': 'LangGraph',
        'langchain': 'LangChain',
        'langchain_core': 'LangChain Core',
        'langgraph_sdk': 'LangGraph SDK',
        'langgraph.prebuilt': 'LangGraph Prebuilt',
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'psycopg': 'psycopg (PostgreSQL驱动)',
        'redis': 'Redis客户端',
        'httpx': 'HTTPX',
        'orjson': 'orjson',
        'tenacity': 'Tenacity',
        'cloudpickle': 'cloudpickle',
        'pydantic': 'Pydantic',
        'structlog': 'structlog',
        'pytest': 'Pytest',
    }

    all_ok = True
    for module_name, display_name in required_packages.items():
        try:
            __import__(module_name)
            print(f"  ✅ {display_name}")
        except ImportError as e:
            print(f"  ❌ {display_name} - 未安装或导入失败: {e}")
            all_ok = False

    return all_ok


def check_postgres() -> bool:
    """验证PostgreSQL连接"""
    print_section("3. PostgreSQL连接检查")

    try:
        import psycopg

        # 从环境变量或使用默认值
        db_url = os.getenv(
            'DATABASE_URL',
            'postgresql://bmad_user:bmad_dev_password@localhost:5432/bmad_langgraph_dev'
        )

        conn = psycopg.connect(db_url, connect_timeout=10)
        cursor = conn.cursor()

        # 获取版本信息
        cursor.execute('SELECT version();')
        version = cursor.fetchone()[0].split(',')[0]
        print(f"PostgreSQL版本: {version}")

        # 测试创建表权限
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS _env_test (
                id SERIAL PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        cursor.execute('DROP TABLE _env_test;')
        conn.commit()

        cursor.close()
        conn.close()

        print("✅ PostgreSQL连接成功，权限验证通过")
        return True

    except Exception as e:
        print(f"❌ PostgreSQL连接失败: {e}")
        return False


def check_redis() -> bool:
    """验证Redis连接"""
    print_section("4. Redis连接检查")

    try:
        import redis

        # 从环境变量或使用默认值
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

        r = redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=5)

        # 测试连接
        pong = r.ping()
        if not pong:
            raise Exception("PING失败")

        # 获取版本
        info = r.info('server')
        print(f"Redis版本: {info['redis_version']}")

        # 测试读写
        r.set('_env_test', 'test_value', ex=5)
        value = r.get('_env_test')
        if value != 'test_value':
            raise Exception("读写测试失败")
        r.delete('_env_test')

        r.close()

        print("✅ Redis连接成功，读写测试通过")
        return True

    except Exception as e:
        print(f"❌ Redis连接失败: {e}")
        return False


def check_langgraph_basic() -> bool:
    """验证LangGraph基础功能"""
    print_section("5. LangGraph基础功能检查")

    try:
        from typing import TypedDict
        from langgraph.graph import StateGraph, END

        # 定义状态
        class State(TypedDict):
            message: str
            count: int

        # 定义节点函数
        def increment_node(state: State) -> State:
            return {"count": state["count"] + 1, "message": state["message"]}

        # 创建图
        workflow = StateGraph(State)
        workflow.add_node("increment", increment_node)
        workflow.set_entry_point("increment")
        workflow.add_edge("increment", END)

        # 编译图
        app = workflow.compile()

        # 测试执行
        result = app.invoke({"message": "test", "count": 0})

        if result["count"] != 1:
            raise Exception(f"执行结果不符合预期: count={result['count']}")

        print("StateGraph创建: ✓")
        print("节点执行: ✓")
        print("状态更新: ✓")
        print("✅ LangGraph基础功能正常")
        return True

    except Exception as e:
        print(f"❌ LangGraph功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n" + "🔍 BMAD LangGraph 1.0 环境验证".center(60, "="))

    results = {
        "Python版本": check_python_version(),
        "包安装": check_packages(),
        "PostgreSQL": check_postgres(),
        "Redis": check_redis(),
        "LangGraph功能": check_langgraph_basic(),
    }

    # 打印总结
    print_section("验证总结")

    passed = sum(results.values())
    total = len(results)

    for check, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {check:.<30} {status}")

    print(f"\n验证结果: {passed}/{total} 项通过")

    if passed == total:
        print("\n🎉 所有验证项通过！环境配置正确。\n")
        return 0
    else:
        print("\n⚠️  部分验证项失败，请检查环境配置。\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
