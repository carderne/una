from pathlib import Path

import tomlkit

from una import config, defaults
from una.types import ConfWrapper, Include, Proj


def create_workspace(path: Path, ns: str) -> None:
    app_content = defaults.EXAMPLE_APP_CODE.format(ns=ns, lib_name=defaults.EXAMPLE_LIB_NAME)
    lib_content = defaults.EXAMPLE_LIB_CODE
    dependencies = f'"{defaults.EXAMPLE_IMPORT}"'

    _update_workspace_config(path, ns, defaults.EXAMPLE_IMPORT)
    create_package(path, defaults.EXAMPLE_APP_NAME, defaults.libs_dir, app_content, "")
    create_package(path, defaults.EXAMPLE_LIB_NAME, defaults.libs_dir, lib_content, dependencies)


def parse_package_paths(packages: list[Include]) -> list[Path]:
    sorted_packages = sorted(packages, key=lambda p: p.src)
    return [Path(p.src) for p in sorted_packages]


def get_projects(root: Path) -> list[Proj]:
    root_conf = config.load_conf(root)
    ns = root_conf.project.name
    confs = _get_toml_files(root)
    return [
        Proj(
            name=c.conf.project.name,
            packages=config.get_project_package_includes(ns, c.conf),
            path=c.path,
            ext_deps=config.get_project_dependencies(c.conf),
        )
        for c in confs
    ]


def create_package(path: Path, name: str, top_dir: str, content: str, dependencies: str) -> None:
    conf = config.load_conf(path)
    python_version = conf.project.requires_python
    ns = config.get_ns(path)

    app_dir = _create_dir(path, f"{top_dir}/{name}")
    ns_dir = _create_dir(path, f"{top_dir}/{name}/{ns}")
    code_dir = _create_dir(path, f"{top_dir}/{name}/{ns}/{name}")
    test_dir = _create_dir(path, f"{top_dir}/{name}/tests")

    _create_file(code_dir, "__init__.py", content)
    _create_file(code_dir, "py.typed")
    is_app = False  # TODO
    _create_file(
        test_dir,
        f"test_{name}_import.py",
        content=defaults.EXAMPLE_TEST_CODE.format(ns=ns, name=name),
    )
    pyproj_content = defaults.PYPROJ_TEMPLATE.format(
        name=name, python_version=python_version, dependencies=dependencies
    )
    if is_app:
        _create_file(ns_dir, "py.typed")  # is this necessary? basedpyright thinks so...
        if content:
            pyproj_content += defaults.EXAMPLE_APP_DEPS.format(
                ns=ns, lib_name=defaults.EXAMPLE_LIB_NAME
            )
    _create_file(
        app_dir,
        defaults.PYPROJ_FILE,
        pyproj_content,
    )


def get_libs(root: Path, ns: str) -> list[str]:
    return _get_libs_names(root, ns, top_dir=defaults.libs_dir)


def collect_libs_paths(root: Path, ns: str, libs: set[str]) -> set[Path]:
    return _collect_paths(root, ns, defaults.libs_dir, libs)


def _create_file(path: Path, name: str, content: str | None = None) -> Path:
    fullpath = path / name
    if content:
        with fullpath.open("w", encoding="utf-8") as f:
            f.write(content)
    else:
        fullpath.touch()
    return fullpath


def _create_dir(path: Path, dir_name: str, keep: bool = False) -> Path:
    d = path / dir_name
    d.mkdir(parents=True)
    if keep:
        _create_file(d, defaults.KEEP_FILE)
    return d


def _is_int_dep_dir(p: Path) -> bool:
    return p.is_dir() and p.name not in {"__pycache__", ".venv", ".mypy_cache"}


def _get_libs_dirs(root: Path, top_dir: str, ns: str) -> list[Path]:
    sub = ""
    lib_dir = root / top_dir / sub
    if not lib_dir.exists():
        return []
    return [f for f in lib_dir.iterdir() if _is_int_dep_dir(f)]


def _get_libs_names(root: Path, ns: str, top_dir: str) -> list[str]:
    dirs = _get_libs_dirs(root, top_dir, ns)
    return [d.name for d in dirs]


def _collect_paths(root: Path, ns: str, int_dep: str, packages: set[str]) -> set[Path]:
    p_template = config.get_int_dep_structure(root)
    paths = {p_template.format(int_dep=int_dep, ns=ns, package=p) for p in packages}
    return {Path(root / p) for p in paths}


def _update_workspace_config(path: Path, ns: str, dependencies: str) -> None:
    pyproj = path / defaults.PYPROJ_FILE
    with pyproj.open() as f:
        toml = tomlkit.parse(f.read())
    toml["tool"]["rye"]["virtual"] = True  # type:ignore[reportIndexIssues]
    toml["tool"]["rye"]["workspace"] = {"member": ["apps/*", "libs/*"]}  # type:ignore[reportIndexIssues]
    with pyproj.open("w") as f:
        f.write(tomlkit.dumps(toml))  # type:ignore[reportUnknownMemberType]


def _get_project_roots(root: Path) -> list[Path]:
    prefix = "apps"
    return sorted(root.glob(f"{prefix}/*/"))


def _toml_data(path: Path) -> ConfWrapper:
    return ConfWrapper(conf=config.load_conf(path), path=path)


def _get_toml_files(root: Path) -> list[ConfWrapper]:
    project_files = _get_project_roots(root)
    proj = [_toml_data(p) for p in project_files]
    return proj
