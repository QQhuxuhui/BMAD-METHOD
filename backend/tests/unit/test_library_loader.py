"""
单元测试: LibraryLoader

测试专家库加载器的所有核心功能。
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.app.core.langgraph.library_loader import LibraryLoader, get_library_loader


class TestLibraryLoaderInit:
    """测试LibraryLoader初始化"""

    def test_init_with_valid_path(self):
        """测试使用有效路径初始化"""
        loader = LibraryLoader("backend/knowledge_base/aps")
        assert loader.base_path.exists()
        assert loader.base_path.is_dir()

    def test_init_with_invalid_path_raises_error(self):
        """测试使用无效路径初始化应抛出异常"""
        with pytest.raises(FileNotFoundError):
            LibraryLoader("invalid/path/that/does/not/exist")

    def test_cache_initialized_empty(self):
        """测试缓存初始化为空"""
        loader = LibraryLoader()
        assert loader.get_cache_size() == 0


class TestListLibraries:
    """测试list_libraries()方法"""

    def test_list_libraries_returns_list(self):
        """测试返回库列表"""
        loader = LibraryLoader()
        libraries = loader.list_libraries()
        assert isinstance(libraries, list)
        assert len(libraries) > 0

    def test_list_libraries_contains_expected_libraries(self):
        """测试返回的库包含预期的专家库"""
        loader = LibraryLoader()
        libraries = loader.list_libraries()

        expected_libraries = [
            "algorithm-library",
            "constraint-library",
            "objective-library",
            "domain-library",
        ]

        for expected in expected_libraries:
            assert expected in libraries, f"{expected} not found in libraries"

    def test_list_libraries_sorted(self):
        """测试返回的库列表是排序的"""
        loader = LibraryLoader()
        libraries = loader.list_libraries()
        assert libraries == sorted(libraries)

    def test_list_libraries_excludes_hidden_dirs(self):
        """测试排除隐藏目录"""
        loader = LibraryLoader()
        libraries = loader.list_libraries()

        for lib in libraries:
            assert not lib.startswith('.')


class TestLoadLibrary:
    """测试load_library()方法"""

    def test_load_library_success(self):
        """测试成功加载专家库"""
        loader = LibraryLoader()
        result = loader.load_library("algorithm-library")

        assert isinstance(result, dict)
        assert "name" in result
        assert "path" in result
        assert "readme" in result
        assert "files" in result
        assert "content" in result

        assert result["name"] == "algorithm-library"
        assert isinstance(result["files"], list)
        assert isinstance(result["content"], dict)

    def test_load_library_readme_content(self):
        """测试README内容被正确加载"""
        loader = LibraryLoader()
        result = loader.load_library("algorithm-library")

        assert len(result["readme"]) > 0
        assert "算法" in result["readme"] or "Algorithm" in result["readme"]

    def test_load_library_files_list(self):
        """测试文件列表包含markdown文件"""
        loader = LibraryLoader()
        result = loader.load_library("algorithm-library")

        assert len(result["files"]) > 0
        # 所有文件应该是.md文件
        for file in result["files"]:
            assert file.endswith(".md")

    def test_load_library_content_dict(self):
        """测试content字典包含文件内容"""
        loader = LibraryLoader()
        result = loader.load_library("algorithm-library")

        assert len(result["content"]) > 0
        # content的key应该与files列表匹配
        for file in result["files"]:
            assert file in result["content"]
            assert isinstance(result["content"][file], str)
            assert len(result["content"][file]) > 0

    def test_load_library_nonexistent_raises_error(self):
        """测试加载不存在的库应抛出异常"""
        loader = LibraryLoader()
        with pytest.raises(FileNotFoundError):
            loader.load_library("nonexistent-library")

    def test_load_library_empty_name_raises_error(self):
        """测试空库名应抛出异常"""
        loader = LibraryLoader()
        with pytest.raises(ValueError):
            loader.load_library("")

    def test_load_multiple_libraries(self):
        """测试加载多个库"""
        loader = LibraryLoader()
        libraries_to_test = ["algorithm-library", "constraint-library", "objective-library"]

        for lib_name in libraries_to_test:
            result = loader.load_library(lib_name)
            assert result["name"] == lib_name
            assert len(result["files"]) > 0


class TestGetLibraryContent:
    """测试get_library_content()方法"""

    def test_get_library_content_success(self):
        """测试成功获取文件内容"""
        loader = LibraryLoader()
        content = loader.get_library_content("algorithm-library", "README.md")

        assert isinstance(content, str)
        assert len(content) > 0

    def test_get_library_content_file_not_found(self):
        """测试获取不存在的文件应抛出异常"""
        loader = LibraryLoader()
        with pytest.raises(FileNotFoundError):
            loader.get_library_content("algorithm-library", "nonexistent.md")

    def test_get_library_content_library_not_found(self):
        """测试从不存在的库获取文件应抛出异常"""
        loader = LibraryLoader()
        with pytest.raises(FileNotFoundError):
            loader.get_library_content("nonexistent-library", "README.md")

    def test_get_library_content_subdirectory(self):
        """测试获取子目录中的文件"""
        loader = LibraryLoader()
        # 先获取文件列表找一个子目录中的文件
        lib_data = loader.load_library("algorithm-library")

        # 找一个在子目录中的文件
        subdir_file = None
        for file in lib_data["files"]:
            if "/" in file and file != "README.md":
                subdir_file = file
                break

        if subdir_file:
            content = loader.get_library_content("algorithm-library", subdir_file)
            assert isinstance(content, str)
            assert len(content) > 0


class TestSearchKnowledge:
    """测试search_knowledge()方法"""

    def test_search_knowledge_finds_results(self):
        """测试搜索能找到结果"""
        loader = LibraryLoader()
        results = loader.search_knowledge("算法")

        assert isinstance(results, list)
        assert len(results) > 0

    def test_search_knowledge_result_structure(self):
        """测试搜索结果的结构"""
        loader = LibraryLoader()
        results = loader.search_knowledge("算法")

        if results:
            result = results[0]
            assert "library" in result
            assert "file" in result
            assert "title" in result
            assert "content" in result
            assert "match_count" in result

            assert isinstance(result["match_count"], int)
            assert result["match_count"] > 0

    def test_search_knowledge_sorted_by_match_count(self):
        """测试搜索结果按匹配次数降序排序"""
        loader = LibraryLoader()
        results = loader.search_knowledge("算法")

        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i]["match_count"] >= results[i + 1]["match_count"]

    def test_search_knowledge_empty_query(self):
        """测试空查询返回空结果"""
        loader = LibraryLoader()
        results = loader.search_knowledge("")

        assert isinstance(results, list)
        assert len(results) == 0

    def test_search_knowledge_no_results(self):
        """测试搜索不存在的内容返回空结果"""
        loader = LibraryLoader()
        results = loader.search_knowledge("xyzabc123nonexistent")

        assert isinstance(results, list)
        assert len(results) == 0

    def test_search_knowledge_specific_library(self):
        """测试在特定库中搜索"""
        loader = LibraryLoader()
        results = loader.search_knowledge("算法", library_name="algorithm-library")

        assert isinstance(results, list)
        # 所有结果应该来自algorithm-library
        for result in results:
            assert result["library"] == "algorithm-library"

    def test_search_knowledge_case_insensitive(self):
        """测试搜索不区分大小写"""
        loader = LibraryLoader()
        results_lower = loader.search_knowledge("算法")
        results_upper = loader.search_knowledge("算法")

        # 因为是中文，这个测试可能不太适用，但保留以示例
        # 对于英文关键词，应该不区分大小写
        results_en_lower = loader.search_knowledge("algorithm")
        results_en_upper = loader.search_knowledge("ALGORITHM")

        assert len(results_en_lower) == len(results_en_upper)


class TestCaching:
    """测试缓存机制"""

    def test_cache_increases_after_load(self):
        """测试加载后缓存增加"""
        loader = LibraryLoader()
        initial_size = loader.get_cache_size()

        loader.load_library("algorithm-library")
        after_load_size = loader.get_cache_size()

        assert after_load_size > initial_size

    def test_cache_reuse(self):
        """测试缓存复用（第二次加载应该更快，虽然我们不测速度）"""
        loader = LibraryLoader()

        # 第一次加载
        result1 = loader.load_library("algorithm-library")
        cache_size_after_first = loader.get_cache_size()

        # 第二次加载（应该使用缓存）
        result2 = loader.load_library("algorithm-library")
        cache_size_after_second = loader.get_cache_size()

        # 缓存大小不应该增加
        assert cache_size_after_second == cache_size_after_first
        # 结果应该相同
        assert result1 == result2

    def test_clear_cache(self):
        """测试清空缓存"""
        loader = LibraryLoader()

        loader.load_library("algorithm-library")
        assert loader.get_cache_size() > 0

        loader.clear_cache()
        assert loader.get_cache_size() == 0


class TestGetLibraryLoaderSingleton:
    """测试get_library_loader()单例函数"""

    def test_get_library_loader_returns_instance(self):
        """测试返回LibraryLoader实例"""
        loader = get_library_loader()
        assert isinstance(loader, LibraryLoader)

    def test_get_library_loader_singleton(self):
        """测试单例模式（多次调用返回同一实例）"""
        loader1 = get_library_loader()
        loader2 = get_library_loader()
        assert loader1 is loader2

    def test_get_library_loader_custom_path(self):
        """测试使用自定义路径"""
        loader = get_library_loader(base_path="backend/knowledge_base/aps")
        assert isinstance(loader, LibraryLoader)


class TestErrorHandling:
    """测试错误处理"""

    def test_unicode_decode_error_handling(self):
        """测试处理不同编码的文件"""
        loader = LibraryLoader()
        # 大多数文件应该是UTF-8，但系统应该能处理其他编码
        try:
            result = loader.load_library("algorithm-library")
            assert len(result["files"]) > 0
        except UnicodeDecodeError:
            pytest.fail("Should handle different encodings gracefully")

    def test_load_library_with_missing_readme(self):
        """测试加载缺少README的库（应该警告但不失败）"""
        loader = LibraryLoader()
        # modeling-library可能缺少README
        try:
            result = loader.load_library("modeling-library")
            # 应该成功，但README可能为空
            assert "readme" in result
            # 不强制README必须有内容，只要不报错
        except Exception as e:
            pytest.fail(f"Should handle missing README gracefully: {e}")


# Pytest配置和夹具

@pytest.fixture
def loader():
    """提供一个LibraryLoader实例"""
    return LibraryLoader()


@pytest.fixture
def temp_library():
    """创建一个临时测试库"""
    temp_dir = tempfile.mkdtemp()
    lib_path = Path(temp_dir) / "test-library"
    lib_path.mkdir()

    # 创建README
    (lib_path / "README.md").write_text("# Test Library\n\nThis is a test library.")

    # 创建一个子目录和文件
    subdir = lib_path / "category"
    subdir.mkdir()
    (subdir / "test.md").write_text("# Test Document\n\nTest content with keyword.")

    yield temp_dir

    # 清理
    shutil.rmtree(temp_dir)


class TestWithTempLibrary:
    """使用临时库的测试"""

    def test_load_custom_library(self, temp_library):
        """测试加载自定义库"""
        loader = LibraryLoader(temp_library)
        result = loader.load_library("test-library")

        assert result["name"] == "test-library"
        assert "README.md" in result["files"]
        assert len(result["files"]) == 2  # README.md and category/test.md

    def test_search_in_custom_library(self, temp_library):
        """测试在自定义库中搜索"""
        loader = LibraryLoader(temp_library)
        results = loader.search_knowledge("keyword", library_name="test-library")

        assert len(results) == 1
        assert results[0]["library"] == "test-library"
        assert results[0]["file"] == "category/test.md"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
