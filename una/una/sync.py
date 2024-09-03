from collections.abc import Iterable
from pathlib import Path

from una import config, consts
from una.types import CheckDiff, Conf, UvSourceIsWorkspace


def sync_package(diff: CheckDiff):
    _rewrite_package_pyproj(diff.package.path, diff.int_dep_diff)


def _generate_updated_package(conf: Conf, packages: Iterable[str]) -> str | None:
    for p in packages:
        conf.project.dependencies.append(p)
        conf.tool.uv.sources[p] = UvSourceIsWorkspace(workspace=True)
    return conf.to_str()


def _rewrite_package_pyproj(path: Path, packages: Iterable[str]):
    conf = config.load_conf(path)
    generated = _generate_updated_package(conf, packages)
    if not generated:
        return
    fullpath = path / consts.PYPROJ_FILE
    with fullpath.open("w", encoding="utf-8") as f:
        f.write(generated)
