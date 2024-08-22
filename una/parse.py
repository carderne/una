import ast
from functools import lru_cache
from pathlib import Path

from una.types import Imports


def fetch_all_imports(paths: set[Path]) -> Imports:
    rows = [{p.name: _list_imports(p)} for p in paths]
    return {k: v for row in rows for k, v in row.items()}


def _parse_import(node: ast.Import) -> list[str | None]:
    return [name.name for name in node.names]


def _extract_import_from(node: ast.ImportFrom) -> list[str | None]:
    return [f"{node.module}.{alias.name}" for alias in node.names] if node.names else [node.module]


def _parse_import_from(node: ast.ImportFrom) -> list[str | None]:
    return _extract_import_from(node) if node.module and node.level == 0 else []


def _parse_imports(node: ast.AST) -> list[str | None]:
    if isinstance(node, ast.Import):
        return _parse_import(node)
    if isinstance(node, ast.ImportFrom):
        return _parse_import_from(node)
    return []


@lru_cache
def _parse_module(path: Path) -> ast.AST:
    with open(path.as_posix(), encoding="utf-8", errors="ignore") as f:
        tree = ast.parse(f.read(), path.name)
    return tree


def _extract_imports(path: Path) -> list[str]:
    tree = _parse_module(path)
    return [i for node in ast.walk(tree) for i in _parse_imports(node) if i is not None]


def _list_imports(path: Path) -> set[str]:
    py_modules = path.rglob("*.py")
    extracted = (_extract_imports(m) for m in py_modules)
    flattened = (i for imports in extracted for i in imports)
    return set(flattened)
