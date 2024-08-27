import re
from pathlib import Path

from una import config
from una.types import Conf, ConfWrapper, ExtDep, Include, IntDep, PackageDeps


def get_packages(root: Path, ns: str) -> list[PackageDeps]:
    root_conf = config.load_conf(root)
    ns = root_conf.project.name
    confs = get_package_confs(root)
    packages = [
        PackageDeps(
            name=c.conf.project.name,
            path=c.path,
            ext_deps=_get_package_ext_deps(c.conf),
            int_deps=_get_package_int_deps(c, confs, ns),
        )
        for c in confs
    ]
    return [p for p in packages if Path.cwd().name in p.path.as_posix()]


def get_package_confs(root: Path) -> list[ConfWrapper]:
    members = config.get_members(root)
    packages: list[ConfWrapper] = []
    for glob in members:
        package_files = sorted(root.glob(glob))
        packages.extend([ConfWrapper(conf=config.load_conf(p), path=p) for p in package_files])
    return packages


def _parse_deps_table(dep: str) -> ExtDep | None:
    parts = re.split(r"[\^~=!<>]", dep)
    name, *_ = parts if parts else [""]
    version = str.replace(dep, name, "")
    if name:
        return ExtDep(name, version)
    return None


def _get_package_ext_deps(conf: Conf) -> list[ExtDep]:
    deps = conf.project.dependencies
    items = [_parse_deps_table(dep) for dep in deps]
    items_filt = [it for it in items if it]
    return items_filt


def _get_package_int_deps(
    conf: ConfWrapper,
    all_confs: list[ConfWrapper],
    namespace: str,
) -> list[IntDep]:
    packages = [Include(src=k, dst=v) for k, v in conf.conf.tool.una.deps.items()]
    paths = [(conf.path / p.src).parents[1].resolve() for p in packages]

    all_paths = {Path(c.path) for c in all_confs}
    pkg_deps_paths = sorted(all_paths.intersection(paths))
    pkg_deps = [IntDep(path=Path(p), name=Path(p).name) for p in pkg_deps_paths]

    # add self
    pkg_deps.append(IntDep(path=conf.path, name=conf.conf.project.name))
    return pkg_deps
