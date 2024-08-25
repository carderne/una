from copy import deepcopy
from pathlib import Path

from rich.console import Console

from una import config, defaults, distributions, external_deps, files, lock_files, parse
from una.types import CheckReport, ExtDeps, Imports, Options, OrgImports, Proj


def check_int_ext_deps(root: Path, ns: str, project: Proj, options: Options) -> bool:
    name = config.sanitise_name(project.name)
    int_dep_imports, ext_dep_imports = _collect_all_imports(root, ns, project)
    collected_libs = _collect_known_aliases(project, options)
    details = _create_report(
        project,
        int_dep_imports,
        ext_dep_imports,
        collected_libs,
    )
    num_libs = len(project.int_deps.libs)
    res = all([num_libs == 1, not details.int_dep_diff, not details.ext_dep_diff])
    if not options.quiet:
        _print_one_lib(num_libs, name)
        _print_missing_deps(details.int_dep_diff, name)
        _print_missing_deps(details.ext_dep_diff, name)
        if options.verbose:
            print_int_dep_imports(details.int_dep_imports)
            print_int_dep_imports(details.ext_dep_imports)
    return res


def enriched_with_lock_files_data(projects: list[Proj], is_verbose: bool) -> list[Proj]:
    return [_enriched_with_lock_file_data(p, is_verbose) for p in projects]


def extract_int_deps(paths: set[Path], ns: str) -> Imports:
    all_imports = parse.fetch_all_imports(paths)
    return _extract_int_dep_imports(all_imports, ns)


def with_unknown_libs(root: Path, ns: str, int_dep_imports: Imports) -> Imports:
    keys = set(int_dep_imports.keys())
    values: set[str] = set().union(*int_dep_imports.values())
    unknowns = values.difference(keys)
    if not unknowns:
        return int_dep_imports
    paths = files.collect_libs_paths(root, ns, unknowns)
    extracted = extract_int_deps(paths, ns)
    if not extracted:
        return int_dep_imports
    collected = {**int_dep_imports, **extracted}
    return with_unknown_libs(root, ns, collected)


def imports_diff(int_dep_imports: OrgImports, libs: set[str]) -> set[str]:
    flattened_libs: set[str] = set().union(*int_dep_imports.libs.values())
    return _diff(flattened_libs, libs)


def print_int_dep_imports(int_dep_imports: OrgImports) -> None:
    console = Console(theme=defaults.RICH_THEME)
    libs_imports = int_dep_imports.libs
    for key, values in libs_imports.items():
        imports_in_int_dep = values.difference({key})
        if not imports_in_int_dep:
            continue
        joined = ", ".join(imports_in_int_dep)
        message = f":information: [data]{key}[/] is importing [data]{joined}[/]"
        console.print(message)


def _with_ext_deps_from_lock_file(project: Proj) -> Proj:
    lock_file_path = lock_files.pick_lock_file(project)
    if not lock_file_path:
        return project
    ext_deps = lock_files.extract_libs(lock_file_path)
    project = deepcopy(project)
    project.ext_deps = ExtDeps(source=str(lock_file_path), items=ext_deps)
    return project


def _enriched_with_lock_file_data(project: Proj, is_verbose: bool) -> Proj:
    try:
        return _with_ext_deps_from_lock_file(project)
    except ValueError as e:
        if is_verbose:
            print(f"{project.name}: {e}")
        return project


def _collect_known_aliases(project: Proj, options: Options) -> set[str]:
    return distributions.known_aliases_and_sub_dependencies(project.ext_deps, options.alias)


def _only_int_dep_imports(imports: set[str], top_ns: str) -> set[str]:
    return {i for i in imports if i.startswith(top_ns)}


def _only_int_dep_name(int_dep_imports: set[str]) -> set[str]:
    res = [i.split(".") for i in int_dep_imports]
    return {i[1] for i in res if len(i) > 1}


def _extract_int_dep_imports(all_imports: Imports, top_ns: str) -> Imports:
    only_int = {k: _only_int_dep_imports(v, top_ns) for k, v in all_imports.items()}
    return {k: _only_int_dep_name(v) for k, v in only_int.items() if v}


def _diff(known_int_deps: set[str], libs: set[str]) -> set[str]:
    return known_int_deps.difference(libs)


def _fetch_int_dep_imports(root: Path, ns: str, all_imports: Imports) -> Imports:
    extracted = _extract_int_dep_imports(all_imports, ns)
    res = with_unknown_libs(root, ns, extracted)
    return res


def _print_one_lib(num_libs: int, project_name: str) -> None:
    if num_libs == 1:
        return
    console = Console(theme=defaults.RICH_THEME)
    console.print(f"Projects must include exactly ONE app, but {project_name} has {num_libs}")


def _print_missing_deps(diff: set[str], project_name: str) -> None:
    if not diff:
        return
    console = Console(theme=defaults.RICH_THEME)
    missing = ", ".join(sorted(diff))
    console.print(f":thinking_face: Cannot locate {missing} in {project_name}")


def _collect_all_imports(root: Path, ns: str, project: Proj) -> tuple[OrgImports, OrgImports]:
    libs_pkgs = {c for c in project.int_deps.libs}
    libs_paths = files.collect_libs_paths(root, ns, libs_pkgs)
    all_imports_in_libs = parse.fetch_all_imports(libs_paths)
    int_dep_imports = OrgImports(
        libs=_fetch_int_dep_imports(root, ns, all_imports_in_libs),
    )
    ext_dep_imports = OrgImports(
        libs=external_deps.extract_ext_dep_imports(all_imports_in_libs, ns),
    )
    return int_dep_imports, ext_dep_imports


def _create_report(
    project: Proj,
    int_dep_imports: OrgImports,
    ext_dep_imports: OrgImports,
    third_party_libs: set[str],
) -> CheckReport:
    lib_pkgs = {c for c in project.int_deps.libs}
    int_dep_diff = imports_diff(int_dep_imports, lib_pkgs)
    ext_dep_diff = external_deps.calculate_diff(ext_dep_imports, third_party_libs)
    return CheckReport(
        int_dep_imports=int_dep_imports,
        ext_dep_imports=ext_dep_imports,
        int_dep_diff=int_dep_diff,
        ext_dep_diff=ext_dep_diff,
    )
