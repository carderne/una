from collections.abc import Sequence
from pathlib import Path

from rich.console import Console

from una import check, config, defaults, files, internal_deps
from una.config import load_conf
from una.types import Conf, Diff, Include, Options, Proj, Style


def sync_project_int_deps(root: Path, ns: str, project: Proj, options: Options):
    apps_pkgs = files.get_apps(root, ns)
    libs_pkgs = files.get_libs(root, ns)
    diff = _calculate_diff(root, ns, project, apps_pkgs, libs_pkgs)
    _update_project(ns, diff)
    if options.quiet:
        return
    _print_summary(diff)
    if options.verbose:
        _print_int_dep_imports(diff)


def _calculate_diff(
    root: Path,
    ns: str,
    project: Proj,
    apps_pkgs: Sequence[str],
    libs_pkgs: Sequence[str],
) -> Diff:
    proj_apps = set(project.int_deps.apps)
    proj_libs = set(project.int_deps.libs)
    all_apps = set(apps_pkgs)
    all_libs = set(libs_pkgs)
    int_dep_imports = internal_deps.get_int_dep_imports(root, ns, proj_apps, proj_libs)
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


def _print_int_dep_imports(diff: Diff) -> None:
    int_dep_imports = diff.int_dep_imports
    check.print_int_dep_imports(int_dep_imports)


def _print_summary(diff: Diff) -> None:
    console = Console(theme=defaults.RICH_THEME)
    name = diff.name
    apps_pkgs = diff.apps
    libs_pkgs = diff.libs
    for b in apps_pkgs:
        console.print(f"adding [app]{b}[/] app to [proj]{name}[/]")
    for c in libs_pkgs:
        console.print(f"adding [lib]{c}[/] lib to [proj]{name}[/]")


def _to_package(ns: str, name: str, int_dep_root: str, style: Style) -> Include:
    root = Path(int_dep_root)
    src = root / ns / name if style == Style.modules else root / name / ns / name
    dst = Path(ns) / name
    return Include(src=str(src), dst=str(dst))


def _generate_updated_project(conf: Conf, packages: list[Include]) -> str | None:
    for inc in packages:
        conf.tool.una.deps[inc.src] = inc.dst
    return conf.to_str()


def _to_packages(ns: str, diff: Diff) -> list[Include]:
    root = config.get_workspace_root()
    style = config.get_style(root)
    apps_path = "../../apps"
    libs_path = "../../libs"
    a = [_to_package(ns, b, apps_path, style) for b in diff.apps]
    b = [_to_package(ns, c, libs_path, style) for c in diff.libs]
    return a + b


def _rewrite_project_file(path: Path, packages: list[Include]):
    conf = load_conf(path)
    generated = _generate_updated_project(conf, packages)
    if not generated:
        return
    fullpath = path / defaults.PYPROJ_FILE
    with fullpath.open("w", encoding="utf-8") as f:
        f.write(generated)


def _update_project(ns: str, diff: Diff):
    packages = _to_packages(ns, diff)
    if packages:
        _rewrite_project_file(diff.path, packages)
