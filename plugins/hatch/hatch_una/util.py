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
    try:
        sources: dict[str, dict[str, bool]] = conf["tool"]["uv"]["sources"]
    except KeyError as e:
        raise KeyError(f"No tool.uv.sources table for '{path}'") from e

    ext_deps: list[str] = []
    int_deps: list[str] = []
    for d in all_deps:
        if d in sources:
            if sources[d]["workspace"]:
                int_deps.append(d)
                continue
        ext_deps.append(d.replace(" ", ""))
    return (ext_deps, int_deps)


def find_package_dir(name: str, members: list[str]) -> Path:
    root = get_workspace_root()
    for glob in members:
        packages = sorted(root.glob(glob))
        for p in packages:
            if p.name == name:
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
    elif (cwd / ".git").exists():
        return cwd
    return _find_upwards(cwd.parent)
