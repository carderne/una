from functools import lru_cache
from pathlib import Path

from una import defaults
from una.types import Conf


def load_conf_from_str(s: str) -> Conf:
    return Conf.from_str(s)


@lru_cache
def _load_conf(path: Path) -> Conf:
    # made this private as pyright doesn't seem to like the cache decorator
    with path.open(encoding="utf-8", errors="ignore") as f:
        return load_conf_from_str(f.read())


def load_conf(path: Path) -> Conf:
    fullpath = (path / defaults.PYPROJ_FILE).resolve()
    return _load_conf(fullpath)


def sanitise_name(name: str) -> str:
    return name.replace("-", "_")


def get_ns(path: Path) -> str:
    return sanitise_name(load_conf(path).project.name)


def get_members(path: Path) -> list[str]:
    return load_conf(path).tool.una.members


def get_workspace_root() -> Path:
    cwd = Path.cwd()
    root = _find_upwards_dir(cwd, defaults.ROOT_FILE)
    if not root:
        raise ValueError("Didn't find the workspace root. Expected to find a .git directory.")
    return root


def _is_drive_root(cwd: Path) -> bool:
    return cwd == Path(cwd.root) or cwd == cwd.parent


def _is_repo_root(cwd: Path) -> bool:
    fullpath = cwd / defaults.ROOT_FILE
    return fullpath.exists()


def _find_upwards(cwd: Path, name: str) -> Path | None:
    if _is_drive_root(cwd):
        return None
    fullpath = cwd / name
    if fullpath.exists():
        return fullpath
    if _is_repo_root(cwd):
        return None
    return _find_upwards(cwd.parent, name)


def _find_upwards_dir(cwd: Path, name: str) -> Path | None:
    fullpath = _find_upwards(cwd, name)
    return fullpath.parent if fullpath else None
