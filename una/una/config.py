from functools import lru_cache
from pathlib import Path

from una import consts
from una.types import Conf


def load_conf_from_str(s: str) -> Conf:
    return Conf.from_str(s)


@lru_cache
def _load_conf(path: Path) -> Conf:
    # made this private as pyright doesn't seem to like the cache decorator
    with path.open(encoding="utf-8", errors="ignore") as f:
        return load_conf_from_str(f.read())


def load_conf(path: Path) -> Conf:
    fullpath = (path / consts.PYPROJ_FILE).resolve()
    return _load_conf(fullpath)


def get_ns(path: Path) -> str:
    ns = load_conf(path).tool.una.namespace
    if ns is None:
        raise ValueError("No namespace set in pyproject.toml")
    return ns


def get_members(path: Path) -> list[str]:
    return load_conf(path).tool.uv.workspace.members


def get_workspace_root() -> Path:
    root = _find_upwards(Path.cwd())
    if not root:
        raise ValueError("Didn't find the workspace root. Expected to find a .git directory.")
    return root


def _find_upwards(cwd: Path) -> Path | None:
    if cwd == Path(cwd.root) or cwd == cwd.parent:
        return None
    elif (cwd / consts.ROOT_FILE).exists():
        return cwd
    return _find_upwards(cwd.parent)
