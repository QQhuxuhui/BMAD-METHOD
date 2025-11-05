"""
BMAD LangGraph 1.0 环境配置单元测试

测试覆盖：
1. Python环境配置
2. 关键依赖包导入
3. PostgreSQL数据库连接
4. Redis缓存连接
"""

import sys
import os
import pytest


class TestPythonEnvironment:
    """Python环境配置测试"""

    def test_python_version(self):
        """测试Python版本 >= 3.11"""
        assert sys.version_info.major == 3
        assert sys.version_info.minor >= 11, f"Python版本需要>=3.11，当前{sys.version_info.minor}"

    def test_python_path(self):
        """测试Python路径配置"""
        assert 'langgraph' in sys.executable.lower(), "应该在langgraph虚拟环境中"


class TestPackageImports:
    """依赖包导入测试"""

    def test_langgraph_import(self):
        """测试LangGraph核心包导入"""
        import langgraph
        from langgraph.graph import StateGraph, END
        assert StateGraph is not None
        assert END is not None

    def test_langgraph_prebuilt_import(self):
        """测试LangGraph Prebuilt模块导入"""
        import langgraph.prebuilt
        assert langgraph.prebuilt is not None

    def test_langchain_import(self):
        """测试LangChain包导入"""
        import langchain
        import langchain_core
        from langchain_core.messages import HumanMessage
        assert HumanMessage is not None

    def test_fastapi_import(self):
        """测试FastAPI导入"""
        from fastapi import FastAPI
        import uvicorn
        assert FastAPI is not None
        assert uvicorn is not None

    def test_database_drivers_import(self):
        """测试数据库驱动导入"""
        import psycopg
        import redis
        assert psycopg is not None
        assert redis is not None

    def test_utility_packages_import(self):
        """测试工具包导入"""
        import httpx
        import orjson
        import tenacity
        import cloudpickle
        import pydantic
        import structlog
        assert all([httpx, orjson, tenacity, cloudpickle, pydantic, structlog])


class TestPostgreSQLConnection:
    """PostgreSQL数据库连接测试"""

    @pytest.fixture
    def db_url(self):
        """数据库连接URL"""
        return os.getenv(
            'DATABASE_URL',
            'postgresql://bmad_user:bmad_dev_password@localhost:5432/bmad_langgraph_dev'
        )

    def test_postgres_connection(self, db_url):
        """测试PostgreSQL连接"""
        import psycopg

        conn = psycopg.connect(db_url, connect_timeout=10)
        assert conn is not None

        cursor = conn.cursor()
        cursor.execute('SELECT 1;')
        result = cursor.fetchone()
        assert result[0] == 1

        cursor.close()
        conn.close()

    def test_postgres_version(self, db_url):
        """测试PostgreSQL版本"""
        import psycopg

        conn = psycopg.connect(db_url, connect_timeout=10)
        cursor = conn.cursor()

        cursor.execute('SELECT version();')
        version = cursor.fetchone()[0]
        assert 'PostgreSQL 16' in version

        cursor.close()
        conn.close()

    def test_postgres_permissions(self, db_url):
        """测试数据库权限（创建/删除表）"""
        import psycopg

        conn = psycopg.connect(db_url, connect_timeout=10)
        cursor = conn.cursor()

        # 测试创建表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_permissions (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100)
            );
        ''')

        # 测试插入数据
        cursor.execute('''
            INSERT INTO test_permissions (name) VALUES ('test') RETURNING id;
        ''')
        insert_id = cursor.fetchone()[0]
        assert insert_id > 0

        # 测试查询数据
        cursor.execute('SELECT name FROM test_permissions WHERE id = %s;', (insert_id,))
        name = cursor.fetchone()[0]
        assert name == 'test'

        # 测试删除表
        cursor.execute('DROP TABLE test_permissions;')
        conn.commit()

        cursor.close()
        conn.close()


class TestRedisConnection:
    """Redis缓存连接测试"""

    @pytest.fixture
    def redis_url(self):
        """Redis连接URL"""
        return os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    def test_redis_connection(self, redis_url):
        """测试Redis连接"""
        import redis

        r = redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=5)
        pong = r.ping()
        assert pong is True
        r.close()

    def test_redis_version(self, redis_url):
        """测试Redis版本"""
        import redis

        r = redis.from_url(redis_url, socket_connect_timeout=5)
        info = r.info('server')
        version = info['redis_version']
        assert version.startswith('7.')
        r.close()

    def test_redis_operations(self, redis_url):
        """测试Redis读写操作"""
        import redis

        r = redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=5)

        # 测试SET
        r.set('test_key', 'test_value', ex=60)

        # 测试GET
        value = r.get('test_key')
        assert value == 'test_value'

        # 测试EXISTS
        exists = r.exists('test_key')
        assert exists == 1

        # 测试DELETE
        r.delete('test_key')
        exists = r.exists('test_key')
        assert exists == 0

        r.close()


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, '-v', '--tb=short'])
