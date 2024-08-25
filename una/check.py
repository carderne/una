import difflib
from pathlib import Path

from rich.console import Console

from una import defaults, distributions, files, parse, stdlib
from una.types import CheckDiff, Imports, OrgImports, PackageDeps


def check_package_deps(root: Path, ns: str, package: PackageDeps, alias: list[str]) -> CheckDiff:
    int_dep_imports, ext_dep_imports = _collect_all_imports(root, ns, package)
    collected_libs = distributions.collect_deps(package.ext_deps, alias)
    diff = _create_diff(
        package,
        int_dep_imports,
        ext_dep_imports,
        collected_libs,
    )
    return diff


def print_check_results(diff: CheckDiff) -> None:
    _print_missing_deps(diff.int_dep_diff, diff.package.name)
    _print_missing_deps(diff.ext_dep_diff, diff.package.name)


def _extract_int_deps(paths: set[Path], ns: str) -> Imports:
    all_imports = parse.fetch_all_imports(paths)
    return _extract_int_dep_imports(all_imports, ns)


def _with_unknown_libs(root: Path, ns: str, int_dep_imports: Imports) -> Imports:
    keys = set(int_dep_imports.keys())
    values: set[str] = set().union(*int_dep_imports.values())
    unknowns = values.difference(keys)
    if not unknowns:
        return int_dep_imports
    paths = files.collect_libs_paths(root, ns, unknowns)
    extracted = _extract_int_deps(paths, ns)
    if not extracted:
        return int_dep_imports
    collected = {**int_dep_imports, **extracted}
    return _with_unknown_libs(root, ns, collected)


def _only_int_dep_imports(imports: set[str], top_ns: str) -> set[str]:
    return {i for i in imports if i.startswith(top_ns)}


def _only_int_dep_name(int_dep_imports: set[str]) -> set[str]:
    res = [i.split(".") for i in int_dep_imports]
    return {i[1] for i in res if len(i) > 1}


def _extract_int_dep_imports(all_imports: Imports, top_ns: str) -> Imports:
    only_int = {k: _only_int_dep_imports(v, top_ns) for k, v in all_imports.items()}
    return {k: _only_int_dep_name(v) for k, v in only_int.items() if v}


def _fetch_int_dep_imports(root: Path, ns: str, all_imports: Imports) -> Imports:
    extracted = _extract_int_dep_imports(all_imports, ns)
    res = _with_unknown_libs(root, ns, extracted)
    return res


def _print_missing_deps(diff: set[str], package_name: str) -> None:
    if not diff:
        return
    console = Console(theme=defaults.RICH_THEME)
    missing = ", ".join(sorted(diff))
    console.print(f":thinking_face: Cannot locate {missing} in {package_name}")


def _collect_all_imports(
    root: Path, ns: str, package: PackageDeps
) -> tuple[OrgImports, OrgImports]:
    libs_pkgs = {c for c in package.int_deps.libs}
    libs_paths = files.collect_libs_paths(root, ns, libs_pkgs)
    all_imports_in_libs = parse.fetch_all_imports(libs_paths)
    int_dep_imports = OrgImports(
        libs=_fetch_int_dep_imports(root, ns, all_imports_in_libs),
    )
    ext_dep_imports = OrgImports(
        libs=_extract_ext_dep_imports(all_imports_in_libs, ns),
    )
    return int_dep_imports, ext_dep_imports


def _extract_top_ns_from_imports(imports: set[str]) -> set[str]:
    return {imp.split(".")[0] for imp in imports}


def _extract_ext_dep_imports(all_imports: Imports, top_ns: str) -> Imports:
    std_libs = stdlib.get_stdlib()
    top_level_imports = {k: _extract_top_ns_from_imports(v) for k, v in all_imports.items()}
    to_exclude = std_libs.union({top_ns})
    with_third_party = {k: v - to_exclude for k, v in top_level_imports.items()}
    return {k: v for k, v in with_third_party.items() if v}


def _imports_diff(int_dep_imports: OrgImports, libs: set[str]) -> set[str]:
    diff: set[str] = set().union(*int_dep_imports.libs.values()).difference(libs)
    return diff


def _create_diff(
    package: PackageDeps,
    int_dep_imports: OrgImports,
    ext_dep_imports: OrgImports,
    third_party_libs: set[str],
) -> CheckDiff:
    lib_pkgs = {c for c in package.int_deps.libs}
    int_dep_diff = _imports_diff(int_dep_imports, lib_pkgs)
    ext_dep_diff = _ext_dep_diff(ext_dep_imports, third_party_libs)
    return CheckDiff(
        package=package,
        int_dep_imports=int_dep_imports,
        ext_dep_imports=ext_dep_imports,
        int_dep_diff=int_dep_diff,
        ext_dep_diff=ext_dep_diff,
    )


def _ext_dep_diff(imports: OrgImports, deps: set[str]) -> set[str]:
    libs_imports: set[str] = set().union(*imports.libs.values())
    unknown_imports = libs_imports.difference(deps)
    cutoff = 0.6

    unknowns = {str.lower(u) for u in unknown_imports}
    deps_norm = {str.lower(d).replace("-", "_") for d in deps}
    filtered = {u for u in unknowns if not difflib.get_close_matches(u, deps_norm, cutoff=cutoff)}
    return filtered
