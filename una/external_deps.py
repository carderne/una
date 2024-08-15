import difflib
from functools import reduce
from operator import itemgetter
from pathlib import Path

from rich import box, markup
from rich.console import Console
from rich.padding import Padding
from rich.table import Table

from una import config, defaults, distributions, files, parse, stdlib
from una.types import Imports, Options, OrgImports, Proj, Style


def external_deps_from_all(
    root: Path,
    ns: str,
    projects: list[Proj],
    options: Options,
) -> set[bool]:
    imports = {p.name: get_third_party_imports(root, ns, p) for p in projects}
    flattened = reduce(flatten_imports, imports.values(), OrgImports())
    print_libs_summary()
    print_libs_in_int_deps(flattened)
    return {missing_libs(p, imports, options) for p in projects}


def missing_libs(project: Proj, imports: dict[str, OrgImports], options: Options) -> bool:
    name = config.sanitise_name(project.name)
    deps = project.ext_deps
    int_dep_imports = imports[name]
    libs = distributions.known_aliases_and_sub_dependencies(deps, options.alias)
    return print_missing_installed_libs(
        int_dep_imports,
        libs,
        name,
    )


def flatten_imports(acc: OrgImports, item: OrgImports) -> OrgImports:
    apps_i = item.apps
    libs_i = item.libs
    return OrgImports(
        apps={**acc.apps, **apps_i},
        libs={**acc.libs, **libs_i},
    )


def extract_top_ns_from_imports(imports: set[str]) -> set[str]:
    return {imp.split(".")[0] for imp in imports}


def extract_ext_dep_imports(all_imports: Imports, top_ns: str) -> Imports:
    std_libs = stdlib.get_stdlibs()
    top_level_imports = {k: extract_top_ns_from_imports(v) for k, v in all_imports.items()}
    to_exclude = std_libs.union({top_ns})
    with_third_party = {k: v - to_exclude for k, v in top_level_imports.items()}
    return {k: v for k, v in with_third_party.items() if v}


def _get_third_party_imports(root: Path, paths: set[Path]) -> Imports:
    root = config.get_workspace_root()
    top_ns = config.get_ns(root)
    all_imports = parse.fetch_all_imports(paths)
    return extract_ext_dep_imports(all_imports, top_ns)


def get_third_party_imports(root: Path, ns: str, project: Proj) -> OrgImports:
    apps_d = {b for b in project.int_deps.apps}
    libs_d = {c for c in project.int_deps.libs}
    apps_paths = files.collect_apps_paths(root, ns, apps_d)
    libs_paths = files.collect_libs_paths(root, ns, libs_d)
    apps_imports = _get_third_party_imports(root, apps_paths)
    libs_imports = _get_third_party_imports(root, libs_paths)
    return OrgImports(apps=apps_imports, libs=libs_imports)


def flatten(imports: dict[str, set[str]]) -> set[str]:
    res: set[str] = set().union(*imports.values())
    return res


def calculate_diff(imports: OrgImports, deps: set[str], include_libs: bool) -> set[str]:
    apps_imports = flatten(imports.apps)
    # workspace style doesn't require libs imports to be declared in the app deps
    libs_imports: set[str] = flatten(imports.libs) if include_libs else set()
    flat: set[str] = set().union(apps_imports, libs_imports)
    unknown_imports = flat.difference(deps)
    cutoff = 0.6

    unknowns = {str.lower(u) for u in unknown_imports}
    deps_norm = {str.lower(d).replace("-", "_") for d in deps}
    filtered = {u for u in unknowns if not difflib.get_close_matches(u, deps_norm, cutoff=cutoff)}
    return filtered


def print_libs_summary() -> None:
    console = Console(theme=defaults.una_theme)
    console.print(Padding("[data]Libraries in apps and libs[/]", (1, 0, 0, 0)))


def print_libs_in_int_deps(int_dep_imports: OrgImports) -> None:
    apps_imports = flatten(int_dep_imports.apps)
    libs_imports = flatten(int_dep_imports.libs)
    if not apps_imports and not libs_imports:
        return
    console = Console(theme=defaults.una_theme)
    table = Table(box=box.SIMPLE_HEAD)
    apps_i = int_dep_imports.apps
    libs_i = int_dep_imports.libs
    table.add_column("[data]int_dep[/]")
    table.add_column("[data]library[/]")
    for int_dep, imports in sorted(libs_i.items(), key=itemgetter(0)):
        table.add_row(f"[lib]{int_dep}[/]", ", ".join(sorted(imports)))
    for int_dep, imports in sorted(apps_i.items(), key=itemgetter(0)):
        table.add_row(f"[app]{int_dep}[/]", ", ".join(sorted(imports)))
    console.print(table, overflow="ellipsis")


def print_missing_installed_libs(
    int_dep_imports: OrgImports,
    third_party_libs: set[str],
    project_name: str,
) -> bool:
    root = config.get_workspace_root()
    style = config.get_style(root)
    include_libs = style == Style.modules
    diff = calculate_diff(int_dep_imports, third_party_libs, include_libs)
    if not diff:
        return True
    console = Console(theme=defaults.una_theme)
    missing = ", ".join(sorted(diff))
    console.print(
        f"[data]Could not locate all libraries in [/][proj]{project_name}[/]. [data]Caused by missing dependencies?[/]"
    )
    console.print(f":thinking_face: {missing}")
    return False


def printable_version(version: str | None) -> str:
    if version is None:
        ver = "-"
    elif version == "":
        ver = "✔"
    else:
        ver = version
    return f"[data]{ver}[/]"


def libs_in_projects_table(
    projects: list[Proj],
    libraries: set[str],
    options: Options,
) -> Table:
    table = Table(box=box.SIMPLE_HEAD)
    projects = sorted(projects, key=lambda p: p.name)
    project_headers = [f"[proj]{p.name}[/]" for p in projects]
    headers = ["[data]library[/]"] + project_headers
    for header in headers:
        table.add_column(header)
    for lib in sorted(libraries):
        proj_versions = [p.ext_deps.items.get(lib) for p in projects]
        printable_proj_versions = [printable_version(v) for v in proj_versions]
        cols = [markup.escape(lib)] + printable_proj_versions
        table.add_row(*cols)
    return table


def flattened_lib_names(projects: list[Proj]) -> set[str]:
    return {k for proj in projects for k in proj.ext_deps.items}


def print_libs_in_projects(projects: list[Proj], options: Options) -> None:
    flattened = flattened_lib_names(projects)
    if not flattened:
        return
    table = libs_in_projects_table(projects, flattened, options)
    console = Console(theme=defaults.una_theme)
    console.print(Padding("[data]Libraries in projects[/]", (1, 0, 0, 0)))
    console.print(table, overflow="ellipsis")
