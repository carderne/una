from pathlib import Path

from una import config, consts
from una.types import CheckDiff, Conf, Include, PackageDeps


def sync_package_int_deps(diff: CheckDiff, ns: str):
    packages = [_to_package(diff.package, ns, c) for c in diff.int_dep_diff]
    if packages:
        _rewrite_package_pyproj(diff.package.path, packages)


def _to_package(orig_pkg: PackageDeps, ns: str, name: str) -> Include:
    int_dep_roots = [f for f in orig_pkg.int_deps if f.name == name]
    if len(int_dep_roots) != 1:
        raise ValueError("WTF?")  # TODO
    root = int_dep_roots[0].path
    src = root / name / ns / name
    dst = Path(ns) / name
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
