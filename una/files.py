from pathlib import Path

import tomlkit

from una import config, defaults
from una.types import ConfWrapper, Include, Proj, Style


def create_file(path: Path, name: str, content: str | None = None) -> Path:
    fullpath = path / name
    if content:
        with fullpath.open("w", encoding="utf-8") as f:
            f.write(content)
    else:
        fullpath.touch()
    return fullpath


def create_dir(path: Path, dir_name: str, keep: bool = False) -> Path:
    d = path / dir_name
    d.mkdir(parents=True)
    if keep:
        create_file(d, defaults.keep_file_name)
    return d


def is_int_dep_dir(p: Path) -> bool:
    return p.is_dir() and p.name not in {"__pycache__", ".venv", ".mypy_cache"}


def get_libs_dirs(root: Path, top_dir: str, ns: str) -> list[Path]:
    style = config.get_style(root)
    sub = "" if style == Style.packages else ns
    lib_dir = root / top_dir / sub
    if not lib_dir.exists():
        return []
    return [f for f in lib_dir.iterdir() if is_int_dep_dir(f)]


def get_apps_libs_names(root: Path, ns: str, top_dir: str) -> list[str]:
    dirs = get_libs_dirs(root, top_dir, ns)
    return [d.name for d in dirs]


def get_libs(root: Path, ns: str) -> list[str]:
    return get_apps_libs_names(root, ns, top_dir=defaults.libs_dir)


def get_apps(root: Path, ns: str) -> list[str]:
    return get_apps_libs_names(root, ns, defaults.apps_dir)


def collect_paths(root: Path, ns: str, int_dep: str, packages: set[str]) -> set[Path]:
    p_template = config.get_int_dep_structure(root)
    paths = {p_template.format(int_dep=int_dep, ns=ns, package=p) for p in packages}
    return {Path(root / p) for p in paths}


def collect_apps_paths(root: Path, ns: str, libs: set[str]) -> set[Path]:
    return collect_paths(root, ns, defaults.apps_dir, libs)


def collect_libs_paths(root: Path, ns: str, libs: set[str]) -> set[Path]:
    return collect_paths(root, ns, defaults.libs_dir, libs)


def update_workspace_config(path: Path, ns: str, style: Style) -> None:
    pyproj = path / defaults.pyproj
    if style == Style.modules:
        with pyproj.open() as f:
            toml = tomlkit.parse(f.read())
        toml["tool"]["hatch"]["build"].add("dev-mode-dirs", ["libs", "apps"])  # type:ignore[reportIndexIssues]
        toml["tool"]["una"] = {"style": "modules"}  # type:ignore[reportIndexIssues]
        with pyproj.open("w", encoding="utf-8") as f:
            f.write(tomlkit.dumps(toml))  # type:ignore[reportUnknownMemberType]
    else:
        with pyproj.open() as f:
            toml = tomlkit.parse(f.read())
        toml["tool"]["rye"]["virtual"] = True  # type:ignore[reportIndexIssues]
        toml["tool"]["rye"]["workspace"] = {"member": ["apps/*", "libs/*"]}  # type:ignore[reportIndexIssues]
        toml["tool"]["una"] = {"style": "packages"}  # type:ignore[reportIndexIssues]
        with pyproj.open("w") as f:
            f.write(tomlkit.dumps(toml))  # type:ignore[reportUnknownMemberType]


def create_workspace(path: Path, ns: str, style: Style) -> None:
    update_workspace_config(path, ns, style)

    app_content = defaults.app_template.format(ns=ns, lib_name=defaults.example_lib)
    lib_content = defaults.lib_template
    dependencies = '"cowsay-python==1.0.1"'

    if style == Style.modules:
        create_project(path, "example_project", dependencies)

    if style == Style.packages:
        create_package(path, defaults.example_app, defaults.apps_dir, app_content, "")
        create_package(path, defaults.example_lib, defaults.libs_dir, lib_content, dependencies)
    else:
        create_module(path, defaults.example_app, defaults.apps_dir, app_content)
        create_module(path, defaults.example_lib, defaults.libs_dir, app_content)


def parse_package_paths(packages: list[Include]) -> list[Path]:
    sorted_packages = sorted(packages, key=lambda p: p.src)
    return [Path(p.src) for p in sorted_packages]


def create_project(path: Path, name: str, dependencies: str) -> None:
    conf = config.load_conf(path)
    python_version = conf.project.requires_python

    proj_dir = create_dir(path, f"projects/{name}")
    create_file(
        proj_dir,
        defaults.pyproj,
        defaults.packages_pyproj.format(name=name, python_version=python_version, dependencies=""),
    )


def create_package(path: Path, name: str, top_dir: str, content: str, dependencies: str) -> None:
    conf = config.load_conf(path)
    python_version = conf.project.requires_python
    ns = config.get_ns(path)

    app_dir = create_dir(path, f"{top_dir}/{name}")
    code_dir = create_dir(path, f"{top_dir}/{name}/{ns}/{name}")
    test_dir = create_dir(path, f"{top_dir}/{name}/tests")

    create_file(code_dir, "__init__.py", content)
    create_file(code_dir, "py.typed")
    create_file(test_dir, f"test_{name}_import.py", content=defaults.test_template.format(ns=ns, name=name))
    create_file(
        app_dir,
        defaults.pyproj,
        content=defaults.packages_pyproj.format(name=name, python_version=python_version, dependencies=dependencies),
    )


def create_module(path: Path, name: str, top_dir: str, content: str) -> None:
    ns = config.get_ns(path)
    code_dir = create_dir(path, f"{top_dir}/{ns}/{name}")

    create_file(code_dir, "__init__.py", content)
    create_file(code_dir, f"test_{name}.py", defaults.test_template.format(ns=ns, name=name))


def get_project_roots(root: Path) -> list[Path]:
    ws_root = config.get_workspace_root()
    style = config.get_style(ws_root)
    prefix = "projects" if style == Style.modules else "apps"
    return sorted(root.glob(f"{prefix}/*/"))


def toml_data(path: Path) -> ConfWrapper:
    return ConfWrapper(conf=config.load_conf(path), path=path)


def get_toml_files(root: Path) -> list[ConfWrapper]:
    project_files = get_project_roots(root)
    proj = [toml_data(p) for p in project_files]
    return proj


def get_projects(root: Path) -> list[Proj]:
    root_conf = config.load_conf(root)
    ns = root_conf.project.name
    confs = get_toml_files(root)
    return [
        Proj(
            name=c.conf.project.name,
            packages=config.get_project_package_includes(ns, c.conf),
            path=c.path,
            ext_deps=config.get_project_dependencies(c.conf),
        )
        for c in confs
    ]
