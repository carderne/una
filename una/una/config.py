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


def sanitise_name(name: str) -> str:
    return name.replace("-", "_")


def get_ns(path: Path) -> str:
    return sanitise_name(load_conf(path).project.name)


def get_members(path: Path) -> list[str]:
    return load_conf(path).tool.uv.members


def get_workspace_root() -> Path:
    root = _find_upwards(Path.cwd(), consts.ROOT_FILE)
    if not root:
        raise ValueError("Didn't find the workspace root. Expected to find a .git directory.")
    return root.parent


def _find_upwards(cwd: Path, name: str) -> Path | None:
    if cwd == Path(cwd.root) or cwd == cwd.parent:
        return None
    elif (fullpath := cwd / name).exists():
        return fullpath
    elif (cwd / consts.ROOT_FILE).exists():
        return None
    return _find_upwards(cwd.parent, name)
