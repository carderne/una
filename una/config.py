import re
from functools import lru_cache
from pathlib import Path

from una import defaults
from una.types import Conf, ExtDeps, Include


def load_conf_from_str(s: str) -> Conf:
    return Conf.from_str(s)


@lru_cache
def _load_conf(path: Path) -> Conf:
    # made this private as pyright doesn't seem to like the cache decorator
    with path.open(encoding="utf-8", errors="ignore") as f:
        return load_conf_from_str(f.read())


def clear_conf_cache() -> None:
    _load_conf.cache_clear()


def load_conf(path: Path) -> Conf:
    fullpath = (path / defaults.PYPROJ_FILE).resolve()
    return _load_conf(fullpath)


def get_project_package_includes(namespace: str, conf: Conf) -> list[Include]:
    includes = conf.tool.una.deps
    return [Include(src=k, dst=v) for k, v in includes.items()]


def parse_project_dependencies(conf: Conf) -> dict[str, str]:
    deps = conf.project.dependencies
    return {k: v for dep in deps for k, v in _parse_pep_621_dependency(dep).items()}


def _parse_pep_621_dependency(dep: str) -> dict[str, str]:
    parts = re.split(r"[\^~=!<>]", dep)
    name, *_ = parts if parts else [""]
    version = str.replace(dep, name, "")
    return {name: version} if name else {}


def get_project_dependencies(data: Conf) -> ExtDeps:
    items = parse_project_dependencies(data)
    return ExtDeps(items=items, source=defaults.PYPROJ_FILE)


def sanitise_name(name: str) -> str:
    return name.replace("-", "_")


def get_ns(path: Path) -> str:
    return sanitise_name(load_conf(path).project.name)


def get_int_dep_structure(root: Path) -> str:
    return "{int_dep}/{package}"


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
