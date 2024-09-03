import re
from pathlib import Path

from una import config
from una.types import ConfWrapper, ExtDep, IntDep, PackageDeps


def get_packages(root: Path) -> list[PackageDeps]:
    confs = get_package_confs(root)
    packages = [_get_package_deps(c) for c in confs if Path.cwd().name in c.path.as_posix()]
    return packages


def get_package_confs(root: Path) -> list[ConfWrapper]:
    members = config.get_members(root)
    packages: list[ConfWrapper] = []
    for glob in members:
        package_files = sorted(root.glob(glob))
        packages.extend([ConfWrapper(conf=config.load_conf(p), path=p) for p in package_files])
    return packages


def _parse_deps_table(dep: str) -> ExtDep:
    parts: list[str] = re.split(r"[\^~=!<>]", dep)
    name, *_ = parts if parts else [""]
    version = dep.replace(name, "")
    return ExtDep(name, version)


def _get_package_deps(conf: ConfWrapper) -> PackageDeps:
    items = [_parse_deps_table(dep) for dep in conf.conf.project.dependencies]
    ext_deps: list[ExtDep] = []
    int_deps: list[IntDep] = []
    for it in items:
        if it.name in conf.conf.tool.uv.sources:
            if conf.conf.tool.uv.sources[it.name].workspace:
                int_deps.append(IntDep(name=it.name))
                continue
        ext_deps.append(it)
    return PackageDeps(
        name=conf.conf.project.name,
        path=conf.path,
        ext_deps=ext_deps,
        int_deps=int_deps,
    )
