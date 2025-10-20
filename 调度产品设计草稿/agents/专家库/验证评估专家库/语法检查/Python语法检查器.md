---
module_name: Python语法检查器
category: 语法检查
version: v1.0.0
updated: 2025-10-10
---

# Python语法检查器

## 目标

- 对生成的Python算法代码执行语法级快速校验，返回是否通过及错误明细。

## 接口

```python
def check_syntax(code: str) -> dict:
    """返回 {ok: bool, errors: [str]}"""
```

## 参考实现

```python
import ast

def check_syntax(code: str) -> dict:
    try:
        ast.parse(code)
        return {"ok": True, "errors": []}
    except SyntaxError as e:
        return {"ok": False, "errors": [f"{e.msg} at line {e.lineno}"]}
```
