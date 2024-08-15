from functools import reduce  # noqa: I001
from pathlib import Path

from rich import box
from rich.console import Console
from rich.padding import Padding
from rich.table import Table

from una import check, config, files, defaults
from una.types import Imports, Include, IntDeps, OrgImports, Proj, Style


def int_cross_deps(root: Path, ns: str) -> None:
    apps = set(files.get_apps(root, ns))
    libs = set(files.get_libs(root, ns))
    int_dep_imports = get_int_dep_imports(root, ns, apps, libs)
    imports = {**int_dep_imports.apps, **int_dep_imports.libs}

    flattened = flatten_imports(imports)
    imported_apps = sorted({b for b in flattened if b in apps})
    imported_libs = sorted({c for c in flattened if c in libs})
    imported_int_deps = imported_libs + imported_apps
    table = Table(box=box.SIMPLE_HEAD)
    table.add_column("[data]int_dep[/]")
    cols = create_columns(imported_apps, imported_libs)
    rows = create_rows(apps, libs, imports, imported_int_deps)
    for col in cols:
        table.add_column(col, justify="center")
    for row in rows:
        table.add_row(*row)
    console = Console(theme=defaults.una_theme)
    console.print(Padding("[data]Internal libs in libs and apps[/]", (1, 0, 0, 0)))
    console.print(table, overflow="ellipsis")


def get_int_dep_imports(root: Path, ns: str, apps: set[str], libs: set[str]) -> OrgImports:
    apps_paths = files.collect_apps_paths(root, ns, apps)
    comp_paths = files.collect_libs_paths(root, ns, libs)
    int_dep_imports_in_apps = check.extract_int_deps(apps_paths, ns)
    int_dep_imports_in_libs = check.extract_int_deps(comp_paths, ns)
    return OrgImports(
        apps=check.with_unknown_libs(root, ns, int_dep_imports_in_apps),
        libs=check.with_unknown_libs(root, ns, int_dep_imports_in_libs),
    )


def to_col(int_dep: str, tag: str) -> str:
    return f"[{tag}]{int_dep}[/]"


def int_dep_status_matrix(int_deps: set[str], int_dep_name: str, imported: str) -> str:
    status = ":heavy_check_mark:" if imported in int_deps and imported != int_dep_name else "-"
    return f"[data]{status}[/]"


def to_row(name: str, tag: str, int_dep_imports: Imports, imported: list[str]) -> list[str]:
    int_deps = int_dep_imports.get(name) or set()
    statuses = [int_dep_status_matrix(int_deps, name, i) for i in imported]
    return [f"[{tag}]{name}[/]"] + statuses


def flatten_import(acc: set[str], kv: tuple[str, set[str]]) -> set[str]:
    key = kv[0]
    values = kv[1]
    res: set[str] = set().union(acc, values.difference({key}))
    return res


def flatten_imports(int_dep_imports: Imports) -> set[str]:
    """Flatten the dict into a set of imports, with the actual int_dep filtered away when existing as an import"""
    return reduce(flatten_import, int_dep_imports.items(), set())


def create_columns(imported_apps: list[str], imported_libs: list[str]) -> list[str]:
    app_cols = [to_col(int_dep, "app") for int_dep in imported_apps]
    lib_cols = [to_col(int_dep, "lib") for int_dep in imported_libs]
    return lib_cols + app_cols


def create_rows(apps: set[str], libs: set[str], import_data: Imports, imported: list[str]) -> list[list[str]]:
    app_rows = [to_row(b, "app", import_data, imported) for b in sorted(apps)]
    lib_rows = [to_row(c, "lib", import_data, imported) for c in sorted(libs)]
    return lib_rows + app_rows


def int_deps_from_projects(root: Path, ns: str) -> None:
    apps = files.get_apps(root, ns)
    libs = files.get_libs(root, ns)
    if not libs and not apps:
        return
    projects = get_int_deps_in_projects(root, libs, apps, ns)
    table = build_int_deps_in_projects_table(projects, apps, libs)
    console = Console(theme=defaults.una_theme)
    console.print(Padding("[data]Internal deps in projects[/]", (1, 0, 0, 0)))
    console.print(table, overflow="ellipsis")


def get_matching_int_deps(paths: list[Path], int_deps: list[str], namespace: str) -> list[str]:
    paths_in_namespace = [p.name for p in paths if p.parent.name == namespace]
    res = set(int_deps).intersection(paths_in_namespace)
    return sorted(list(res))


def get_project_int_deps(
    project_packages: list[Include],
    libs_paths: list[str],
    apps_paths: list[str],
    namespace: str,
    self_name: str,
    add_self: bool,
) -> IntDeps:
    paths = files.parse_package_paths(project_packages)
    libs_in_project = get_matching_int_deps(paths, libs_paths, namespace)
    apps_in_project = get_matching_int_deps(paths, apps_paths, namespace)
    if add_self:
        apps_in_project.append(self_name)
    return IntDeps(libs=libs_in_project, apps=apps_in_project)


def get_int_deps_in_projects(root: Path, libs_paths: list[str], apps_paths: list[str], namespace: str) -> list[Proj]:
    packages = files.get_projects(root)
    ws_root = config.get_workspace_root()
    style = config.get_style(ws_root)
    add_self = style == Style.packages
    res = [
        Proj(
            name=p.name,
            packages=p.packages,
            path=p.path,
            ext_deps=p.ext_deps,
            int_deps=get_project_int_deps(
                p.packages,
                libs_paths,
                apps_paths,
                namespace,
                p.name,
                add_self,
            ),
        )
        for p in packages
    ]
    return res


def get_projects_data(root: Path, ns: str) -> list[Proj]:
    app_names = files.get_apps(root, ns)
    lib_names = files.get_libs(root, ns)
    return get_int_deps_in_projects(root, lib_names, app_names, ns)


def int_dep_status_projects(int_dep: str, int_deps: list[str], for_info: bool) -> str:
    emoji = ":heavy_check_mark:" if for_info else ":gear:"
    status = emoji if int_dep in int_deps else "-"
    return f"[data]{status}[/]"


def build_int_deps_in_projects_table(
    projects_data: list[Proj],
    apps: list[str],
    libs: list[str],
    for_info: bool = True,
) -> Table:
    table = Table(box=box.SIMPLE_HEAD)
    table.add_column("[data]int_dep[/]")
    proj_cols = [f"[proj]{p.name}[/]" for p in projects_data]
    for col in proj_cols:
        table.add_column(col, justify="center")
    for int_dep in sorted(libs):
        statuses = [int_dep_status_projects(int_dep, p.int_deps.libs, for_info) for p in projects_data]
        cols = [f"[lib]{int_dep}[/]"] + statuses
        table.add_row(*cols)
    for int_dep in sorted(apps):
        statuses = [int_dep_status_projects(int_dep, p.int_deps.apps, for_info) for p in projects_data]
        cols = [f"[app]{int_dep}[/]"] + statuses
        table.add_row(*cols)
    return table
