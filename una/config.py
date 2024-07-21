import re
from functools import lru_cache
from pathlib import Path
from typing import cast

from una import defaults
from una.types import Conf, ExtDeps, Style


def load_conf_from_str(s: str) -> Conf:
    return Conf.from_str(s)


@lru_cache
def load_conf(path: Path) -> Conf:
    fullpath = path / defaults.pyproj
    with fullpath.open(encoding="utf-8", errors="ignore") as f:
        return load_conf_from_str(f.read())


def transform_to_package(namespace: str, include: str) -> dict[str, str]:
    path, _, int_dep = str.partition(include, f"/{namespace}/")
    return {"include": f"{namespace}/{int_dep}", "from": path}


def get_project_package_includes(namespace: str, conf: Conf) -> list[dict[str, str]]:
    includes = conf.tool.una.libs
    return [transform_to_package(namespace, key) for key in includes.keys()]


def parse_pep_621_dependency(dep: str) -> dict[str, str]:
    parts = re.split(r"[\^~=!<>]", dep)
    name, *_ = parts if parts else [""]
    version = str.replace(dep, name, "")
    return {name: version} if name else {}


def get_pep_621_optional_dependencies(conf: Conf) -> list[str]:
    groups = conf.project.optional_dependencies
    matrix = [v for v in groups.values()] if isinstance(groups, dict) else []
    return sum(matrix, cast(list[str], []))


def parse_project_dependencies(conf: Conf) -> dict[str, str]:
    deps = conf.project.dependencies
    optional_deps = get_pep_621_optional_dependencies(conf)
    all_deps = deps + optional_deps
    return {k: v for dep in all_deps for k, v in parse_pep_621_dependency(dep).items()}


def get_project_dependencies(data: Conf) -> ExtDeps:
    items = parse_project_dependencies(data)
    return ExtDeps(items=items, source=defaults.pyproj)


def get_ns() -> str:
    path = get_workspace_root()
    return load_conf(path).project.name


def get_style() -> Style:
    path = get_workspace_root()
    return load_conf(path).tool.una.style


def get_tag_pattern(key: str | None) -> str:
    return "v*"


def get_tag_sort_options() -> list[str]:
    return ["-committerdate"]


def get_int_dep_structure(root: Path) -> str:
    root_conf = load_conf(root)
    style = root_conf.tool.una.style
    if style == Style.packages:
        return "{int_dep}/{package}"
    else:
        return "{int_dep}/{ns}/{package}"


def is_drive_root(cwd: Path) -> bool:
    return cwd == Path(cwd.root) or cwd == cwd.parent


def is_repo_root(cwd: Path) -> bool:
    fullpath = cwd / defaults.root_file
    return fullpath.exists()


def find_upwards(cwd: Path, name: str) -> Path | None:
    if is_drive_root(cwd):
        return None
    fullpath = cwd / name
    if fullpath.exists():
        return fullpath
    if is_repo_root(cwd):
        return None
    return find_upwards(cwd.parent, name)


def find_upwards_dir(cwd: Path, name: str) -> Path | None:
    fullpath = find_upwards(cwd, name)
    return fullpath.parent if fullpath else None


def get_workspace_root() -> Path:
    cwd = Path.cwd()
    root = find_upwards_dir(cwd, defaults.root_file)
    if not root:
        raise ValueError("Didn't find the workspace root. Expected to find a .git directory.")
    return root


def get_authors(conf: Conf) -> str:
    strings = [f"""{{name = "{a.name}", email = "{a.email}"}}""" for a in conf.project.authors]
    joined = ",".join(strings)
    return f"[{joined}]"
