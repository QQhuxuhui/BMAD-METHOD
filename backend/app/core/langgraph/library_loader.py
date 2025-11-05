"""
专家库加载器模块

提供动态加载和管理BMAD专家知识库的功能。
支持加载、搜索和缓存专家库内容。
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


class LibraryLoader:
    """专家库加载器 - 动态加载BMAD专家知识库"""

    def __init__(self, base_path: str = "backend/knowledge_base/aps"):
        """初始化加载器

        Args:
            base_path: 专家库根目录路径
        """
        self.base_path = Path(base_path)
        if not self.base_path.exists():
            logger.warning(f"Knowledge base path does not exist: {self.base_path}")
            # 尝试相对于当前文件的路径
            alt_path = Path(__file__).parent.parent.parent.parent.parent / "knowledge_base" / "aps"
            if alt_path.exists():
                self.base_path = alt_path
                logger.info(f"Using alternative path: {self.base_path}")
            else:
                raise FileNotFoundError(f"Cannot find knowledge base at {base_path} or {alt_path}")

        self._cache: Dict[str, str] = {}
        logger.info(f"LibraryLoader initialized with base_path: {self.base_path}")

    def load_library(self, library_name: str) -> Dict[str, Any]:
        """加载指定专家库

        Args:
            library_name: 库名称（如 "algorithm-library"）

        Returns:
            {
                "name": str,              # 库名称
                "path": str,              # 库路径
                "readme": str,            # README内容
                "files": List[str],       # 所有文件列表
                "content": Dict[str, str] # 文件内容字典 {相对路径: 内容}
            }

        Raises:
            FileNotFoundError: 如果库不存在
            ValueError: 如果库名称无效
        """
        if not library_name:
            raise ValueError("Library name cannot be empty")

        library_path = self.base_path / library_name

        if not library_path.exists():
            raise FileNotFoundError(f"Library not found: {library_name} at {library_path}")

        if not library_path.is_dir():
            raise ValueError(f"Library path is not a directory: {library_path}")

        logger.info(f"Loading library: {library_name}")

        # 读取README.md
        readme_path = library_path / "README.md"
        readme_content = ""
        if readme_path.exists():
            readme_content = self._read_file_cached(readme_path)
        else:
            logger.warning(f"README.md not found in {library_name}")

        # 收集所有markdown文件
        md_files = list(library_path.rglob("*.md"))
        file_list = [str(f.relative_to(library_path)) for f in md_files]

        # 加载所有文件内容
        content = {}
        for file_path in md_files:
            rel_path = str(file_path.relative_to(library_path))
            content[rel_path] = self._read_file_cached(file_path)

        result = {
            "name": library_name,
            "path": str(library_path),
            "readme": readme_content,
            "files": file_list,
            "content": content
        }

        logger.info(f"Successfully loaded library {library_name} with {len(file_list)} files")
        return result

    def get_library_content(self, library_name: str, file_path: str) -> str:
        """获取库中特定文件内容

        Args:
            library_name: 库名称
            file_path: 相对文件路径（相对于库根目录）

        Returns:
            文件内容字符串

        Raises:
            FileNotFoundError: 如果文件不存在
        """
        full_path = self.base_path / library_name / file_path

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {library_name}/{file_path}")

        return self._read_file_cached(full_path)

    def list_libraries(self) -> List[str]:
        """列出所有可用的专家库

        Returns:
            库名称列表（按字母顺序排序）
        """
        if not self.base_path.exists():
            logger.error(f"Base path does not exist: {self.base_path}")
            return []

        libraries = []
        for item in self.base_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                libraries.append(item.name)

        libraries.sort()
        logger.info(f"Found {len(libraries)} libraries: {libraries}")
        return libraries

    def search_knowledge(self, query: str, library_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """搜索知识库

        Args:
            query: 搜索关键词
            library_name: 限定搜索的库（可选，不指定则搜索所有库）

        Returns:
            匹配的知识点列表，每项包含:
            {
                "library": str,       # 库名称
                "file": str,          # 文件路径
                "title": str,         # 匹配的标题或段落
                "content": str,       # 匹配的内容片段
                "match_count": int    # 匹配次数
            }
        """
        if not query:
            return []

        query_lower = query.lower()
        results = []

        # 确定搜索范围
        libraries_to_search = [library_name] if library_name else self.list_libraries()

        for lib in libraries_to_search:
            try:
                library_data = self.load_library(lib)
                for file_rel_path, content in library_data["content"].items():
                    # 统计匹配次数
                    match_count = content.lower().count(query_lower)

                    if match_count > 0:
                        # 提取匹配的上下文（前后100字符）
                        content_lower = content.lower()
                        match_pos = content_lower.find(query_lower)

                        start = max(0, match_pos - 100)
                        end = min(len(content), match_pos + len(query) + 100)
                        snippet = content[start:end].strip()

                        # 提取标题（第一行）
                        title = content.split('\n')[0].strip('#').strip()

                        results.append({
                            "library": lib,
                            "file": file_rel_path,
                            "title": title,
                            "content": snippet,
                            "match_count": match_count
                        })

            except Exception as e:
                logger.error(f"Error searching in library {lib}: {e}")
                continue

        # 按匹配次数降序排序
        results.sort(key=lambda x: x["match_count"], reverse=True)

        logger.info(f"Search for '{query}' found {len(results)} results")
        return results

    def _read_file_cached(self, file_path: Path) -> str:
        """读取文件内容并缓存

        Args:
            file_path: 文件路径对象

        Returns:
            文件内容字符串
        """
        cache_key = str(file_path)

        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 缓存内容
            self._cache[cache_key] = content
            return content

        except UnicodeDecodeError:
            # 尝试其他编码
            logger.warning(f"UTF-8 decode failed for {file_path}, trying GB18030")
            with open(file_path, 'r', encoding='gb18030') as f:
                content = f.read()

            self._cache[cache_key] = content
            return content

        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise

    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()
        logger.info("Cache cleared")

    def get_cache_size(self) -> int:
        """获取缓存中的文件数量"""
        return len(self._cache)


# 全局单例实例
_global_loader: Optional[LibraryLoader] = None


def get_library_loader(base_path: Optional[str] = None) -> LibraryLoader:
    """获取全局LibraryLoader实例（单例模式）

    Args:
        base_path: 可选的自定义基础路径

    Returns:
        LibraryLoader实例
    """
    global _global_loader

    if _global_loader is None or base_path is not None:
        if base_path:
            _global_loader = LibraryLoader(base_path)
        else:
            _global_loader = LibraryLoader()

    return _global_loader
