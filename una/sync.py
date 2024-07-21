from collections.abc import Sequence
from copy import deepcopy
from functools import reduce
from pathlib import Path

from rich.console import Console

from una import check, defaults, files, internal_deps
from una.config import load_conf
from una.types import Conf, Diff, Options, Proj


def sync_project_int_deps(root: Path, ns: str, project: Proj, options: Options):
    apps_pkgs = files.get_apps(root, ns)
    libs_pkgs = files.get_libs(root, ns)
    diff = calculate_diff(root, ns, project, apps_pkgs, libs_pkgs)
    update_project(ns, diff)
    if options.quiet:
        return
    print_summary(diff)
    if options.verbose:
        print_int_dep_imports(diff)


def calculate_diff(
    root: Path,
    namespace: str,
    project: Proj,
    apps_pkgs: Sequence[str],
    libs_pkgs: Sequence[str],
) -> Diff:
    proj_apps = set(project.int_deps.apps)
    proj_libs = set(project.int_deps.libs)
    all_apps = set(apps_pkgs)
    all_libs = set(libs_pkgs)
    int_dep_imports = internal_deps.get_int_dep_imports(root, namespace, proj_apps, proj_libs)
    int_dep_diff = check.imports_diff(int_dep_imports, proj_apps, proj_libs)
    apps_diff = {b for b in int_dep_diff if b in all_apps}
    libs_diff = {b for b in int_dep_diff if b in all_libs}
    return Diff(
        name=project.name,
        path=project.path,
        apps=apps_diff,
        libs=libs_diff,
        int_dep_imports=int_dep_imports,
    )


def print_int_dep_imports(diff: Diff) -> None:
    int_dep_imports = diff.int_dep_imports
    check.print_int_dep_imports(int_dep_imports)


def print_summary(diff: Diff) -> None:
    console = Console(theme=defaults.una_theme)
    name = diff.name
    apps_pkgs = diff.apps
    libs_pkgs = diff.libs
    anything_to_sync = apps_pkgs or libs_pkgs
    emoji = ":point_right:" if anything_to_sync else ":heavy_check_mark:"
    printable_name = f"[proj]{name}[/]"
    console.print(f"{emoji} {printable_name}")
    for b in apps_pkgs:
        console.print(f"adding [app]{b}[/] app to [proj]{name}[/]")
    for c in libs_pkgs:
        console.print(f"adding [lib]{c}[/] lib to [proj]{name}[/]")
    if anything_to_sync:
        console.print("")


def to_package(namespace: str, int_dep: str, int_dep_path: str) -> dict[str, str]:
    folder = f"{int_dep_path}"
    return {"include": f"{namespace}/{int_dep}", "from": folder}


def to_key_value_include(acc: dict[str, str], package: dict[str, str]) -> dict[str, str]:
    int_dep = package["include"]
    relative_path = package.get("from", "")
    include = Path(relative_path, int_dep).as_posix()
    return {**acc, **{include: int_dep}}


def generate_updated_project(conf: Conf, packages: list[dict[str, str]]) -> str | None:
    int_deps_to_add = reduce(to_key_value_include, packages, {})
    conf = deepcopy(conf)
    for k, v in int_deps_to_add.items():
        conf.tool.una.libs[k] = v
    return conf.to_str()


def to_packages(namespace: str, diff: Diff) -> list[dict[str, str]]:
    apps_path = "../../apps"
    libs_path = "../../libs"
    a = [to_package(namespace, b, apps_path) for b in diff.apps]
    b = [to_package(namespace, c, libs_path) for c in diff.libs]
    return a + b


def rewrite_project_file(path: Path, packages: list[dict[str, str]]):
    conf = load_conf(path)
    generated = generate_updated_project(conf, packages)
    if not generated:
        return
    fullpath = path / defaults.pyproj
    with fullpath.open("w", encoding="utf-8") as f:
        f.write(generated)


def update_project(namespace: str, diff: Diff):
    packages = to_packages(namespace, diff)
    if packages:
        rewrite_project_file(diff.path, packages)
