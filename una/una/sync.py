from pathlib import Path
from typing import cast

from una import config, consts, package_deps
from una.types import CheckDiff, Conf, Include


def sync_package(root: Path, diff: CheckDiff, ns: str):
    all_confs = package_deps.get_package_confs(root)
    pkg_map = {c.path.name: c.path for c in all_confs}
    packages = [_to_package(pkg_map, ns, name, diff.package.path) for name in diff.int_dep_diff]
    _rewrite_package_pyproj(diff.package.path, packages)


def _to_package(pkg_map: dict[str, Path], ns: str, name: str, caller_path: Path) -> Include:
    dst = Path(ns) / name
    src = _path_relative_to(pkg_map[name] / dst, caller_path)
    return Include(src=str(src), dst=str(dst))


def _generate_updated_package(conf: Conf, packages: list[Include]) -> str | None:
    for inc in packages:
        conf.tool.una.deps[inc.src] = inc.dst
    return conf.to_str()


def _rewrite_package_pyproj(path: Path, packages: list[Include]):
    conf = config.load_conf(path)
    generated = _generate_updated_package(conf, packages)
    if not generated:
        return
    fullpath = path / consts.PYPROJ_FILE
    with fullpath.open("w", encoding="utf-8") as f:
        f.write(generated)


def _path_relative_to(p: Path, other: Path) -> Path:
    """
    Return relative path between paths.

    Added here since the walk_up parameter isn't available in Python 3.11
    https://github.com/python/cpython/blob/33d9e27b2b26d5434d654ef8e5fae560beb68b1b/Lib/pathlib.py#L663
    """
    for step, path in enumerate([other] + list(other.parents)):
        if p.is_relative_to(path):
            break
        elif path.name == "..":
            raise ValueError(f"'..' segment in {str(other)!r} cannot be walked")
    else:
        raise ValueError(f"{str(p)!r} and {str(other)!r} have different anchors")
    parts = cast(str, [".."] * step + p._tail[len(path._tail) :])  # pyright:ignore[reportUnknownMemberType,reportAttributeAccessIssue,reportUnknownArgumentType]
    return Path(*parts)
