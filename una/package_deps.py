import re
from pathlib import Path

from una import config, defaults
from una.types import Conf, ConfWrapper, ExtDep, ExtDeps, Include, IntDeps, PackageDeps


def get_packages(root: Path, ns: str) -> list[PackageDeps]:
    lib_names = _get_libs(root, ns)
    root_conf = config.load_conf(root)
    ns = root_conf.project.name
    members = root_conf.tool.una.members
    confs = _get_toml_files(root, members)
    packages = [
        PackageDeps(
            name=c.conf.project.name,
            path=c.path,
            ext_deps=_get_package_ext_deps(c.conf),
            int_deps=_get_package_int_deps(c.conf, lib_names, ns),
        )
        for c in confs
    ]
    return [p for p in packages if Path.cwd().name in p.path.as_posix()]


def _parse_deps_table(dep: str) -> ExtDep | None:
    parts = re.split(r"[\^~=!<>]", dep)
    name, *_ = parts if parts else [""]
    version = str.replace(dep, name, "")
    if name:
        return ExtDep(name, version)
    return None


def _get_package_ext_deps(conf: Conf) -> ExtDeps:
    deps = conf.project.dependencies
    items = [_parse_deps_table(dep) for dep in deps]
    items_filt = [it for it in items if it]
    return ExtDeps(items=items_filt, source=defaults.PYPROJ_FILE)


def _get_toml_files(root: Path, members: list[str]) -> list[ConfWrapper]:
    projects: list[ConfWrapper] = []
    for glob in members:
        package_files = sorted(root.glob(glob))
        projects.extend([ConfWrapper(conf=config.load_conf(p), path=p) for p in package_files])
    return projects


def _get_package_int_deps(
    conf: Conf,
    libs_paths: list[str],
    namespace: str,
) -> IntDeps:
    self_name = conf.project.name
    packages = [Include(src=k, dst=v) for k, v in conf.tool.una.deps.items()]
    sorted_packages = sorted(packages, key=lambda p: p.src)
    paths = [Path(p.src) for p in sorted_packages]
    paths_in_namespace = [p.name for p in paths if p.parent.name == namespace]
    libs_in_project = sorted(list(set(libs_paths).intersection(paths_in_namespace)))
    libs_in_project.append(self_name)
    return IntDeps(libs=libs_in_project)


def _get_libs_dirs(root: Path, top_dir: str, ns: str) -> list[Path]:
    sub = ""
    lib_dir = root / top_dir / sub
    if not lib_dir.exists():
        return []
    return [f for f in lib_dir.iterdir() if _is_int_dep_dir(f)]


def _is_int_dep_dir(p: Path) -> bool:
    return p.is_dir() and p.name not in {"__pycache__", ".venv", ".mypy_cache"}


def _get_libs_names(root: Path, ns: str, top_dir: str) -> list[str]:
    dirs = _get_libs_dirs(root, top_dir, ns)
    return [d.name for d in dirs]


def _get_libs(root: Path, ns: str) -> list[str]:
    return _get_libs_names(root, ns, top_dir=defaults.libs_dir)
