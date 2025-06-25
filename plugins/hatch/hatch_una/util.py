import re
import tomllib
from pathlib import Path
from typing import Any


PYPROJ = "pyproject.toml"


def load_conf(path: Path) -> dict[str, Any]:
    with (path / PYPROJ).open("rb") as fp:
        return tomllib.load(fp)


def get_members() -> list[str]:
    root = get_workspace_root()
    root_conf = load_conf(root)
    members: list[str] = (
        root_conf.get("tool", {}).get("uv", {}).get("workspace", {}).get("members", [])  # pyright:ignore[reportAny]
    )
    return members


def get_dependencies(path: Path) -> tuple[list[str], list[str]]:
    conf = load_conf(path)
    all_deps: list[str] = conf["project"].get("dependencies", [])  # pyright:ignore[reportAny]
    sources: dict[str, dict[str, bool]] = conf.get("tool", {}).get("uv", {}).get("sources", {})  # pyright:ignore[reportAny]

    sources = {_clean_dependency_name(k): v for k, v in sources.items()}

    ext_deps: list[str] = []
    int_deps: list[str] = []
    for d in all_deps:
        cleaned_dependency = _clean_dependency_name(d)
        if cleaned_dependency in sources:
            if sources[cleaned_dependency].get("workspace", False):
                int_deps.append(cleaned_dependency)
                continue
        ext_deps.append(d)
    return (ext_deps, int_deps)


def _clean_dependency_name(dep: str) -> str:
    """
    python allows the interchange of underscores and dashes,
    and the dependencies section could contain version specifiers.
    Remove all such information before matching
    """
    dep = dep.replace("-", "_")
    dep = re.sub(r"[^a-zA-Z0-9_].*", "", dep)
    return dep


def find_package_dir(name: str, members: list[str]) -> Path:
    cleaned_name = _clean_dependency_name(name)
    root = get_workspace_root()
    for glob in members:
        packages = sorted(root.glob(glob))
        for p in packages:
            try:
                package_pyproject = tomllib.loads((p / "pyproject.toml").read_text())
            except FileNotFoundError as e:
                e.add_note(f"workspace member points to a location that has no pyproject.toml: {p}")
                raise e
            package_name = str(package_pyproject.get("project", {}).get("name", ""))  # pyright:ignore[reportAny]
            if _clean_dependency_name(package_name) == cleaned_name:
                return p.resolve()
    raise ValueError(f"Couldn't find package '{name}'")


def get_workspace_root() -> Path:
    root = _find_upwards(Path.cwd())
    if not root:
        raise ValueError("Didn't find the workspace root. Expected to find a .git directory.")
    return root


def _find_upwards(cwd: Path) -> Path | None:
    if cwd == Path(cwd.root) or cwd == cwd.parent:
        return None
    elif (pyproject := cwd / "pyproject.toml").exists():
        conf = tomllib.loads(pyproject.read_text())
        if "members" in conf.get("tool", {}).get("uv", {}).get("workspace", {}):  # pyright:ignore[reportAny]
            return cwd
    return _find_upwards(cwd.parent)
