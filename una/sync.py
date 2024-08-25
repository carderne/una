from collections.abc import Sequence
from pathlib import Path

from rich.console import Console

from una import check, defaults, files
from una.config import load_conf
from una.types import Conf, Diff, Include, Options, OrgImports, Proj


def sync_project_int_deps(root: Path, ns: str, project: Proj, options: Options):
    libs_pkgs = files.get_libs(root, ns)
    diff = _calculate_diff(root, ns, project, libs_pkgs)
    _update_project(ns, diff)
    if options.quiet:
        return
    _print_summary(diff)
    _print_int_dep_imports(diff)


def _calculate_diff(
    root: Path,
    ns: str,
    project: Proj,
    libs_pkgs: Sequence[str],
) -> Diff:
    proj_libs = set(project.int_deps.libs)
    all_libs = set(libs_pkgs)
    int_dep_imports = _get_int_dep_imports(root, ns, proj_libs)
    int_dep_diff = check.imports_diff(int_dep_imports, proj_libs)
    libs_diff = {b for b in int_dep_diff if b in all_libs}
    return Diff(
        name=project.name,
        path=project.path,
        libs=libs_diff,
        int_dep_imports=int_dep_imports,
    )


def _get_int_dep_imports(root: Path, ns: str, libs: set[str]) -> OrgImports:
    comp_paths = files.collect_libs_paths(root, ns, libs)
    int_dep_imports_in_libs = check.extract_int_deps(comp_paths, ns)
    return OrgImports(
        libs=check.with_unknown_libs(root, ns, int_dep_imports_in_libs),
    )


def _print_int_dep_imports(diff: Diff) -> None:
    int_dep_imports = diff.int_dep_imports
    check.print_int_dep_imports(int_dep_imports)


def _print_summary(diff: Diff) -> None:
    console = Console(theme=defaults.RICH_THEME)
    name = diff.name
    libs_pkgs = diff.libs
    for c in libs_pkgs:
        console.print(f"adding [lib]{c}[/] lib to [proj]{name}[/]")


def _to_package(ns: str, name: str, int_dep_root: str) -> Include:
    root = Path(int_dep_root)
    src = root / name / ns / name
    dst = Path(ns) / name
    return Include(src=str(src), dst=str(dst))


def _generate_updated_project(conf: Conf, packages: list[Include]) -> str | None:
    for inc in packages:
        conf.tool.una.deps[inc.src] = inc.dst
    return conf.to_str()


def _to_packages(ns: str, diff: Diff) -> list[Include]:
    libs_path = "../../libs"
    return [_to_package(ns, c, libs_path) for c in diff.libs]


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
