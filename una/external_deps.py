import difflib

from una import stdlib
from una.types import Imports, OrgImports


def calculate_diff(imports: OrgImports, deps: set[str]) -> set[str]:
    libs_imports = _flatten(imports.libs)
    unknown_imports = libs_imports.difference(deps)
    cutoff = 0.6

    unknowns = {str.lower(u) for u in unknown_imports}
    deps_norm = {str.lower(d).replace("-", "_") for d in deps}
    filtered = {u for u in unknowns if not difflib.get_close_matches(u, deps_norm, cutoff=cutoff)}
    return filtered


def _extract_top_ns_from_imports(imports: set[str]) -> set[str]:
    return {imp.split(".")[0] for imp in imports}


def extract_ext_dep_imports(all_imports: Imports, top_ns: str) -> Imports:
    std_libs = stdlib.get_stdlib()
    top_level_imports = {k: _extract_top_ns_from_imports(v) for k, v in all_imports.items()}
    to_exclude = std_libs.union({top_ns})
    with_third_party = {k: v - to_exclude for k, v in top_level_imports.items()}
    return {k: v for k, v in with_third_party.items() if v}


def _flatten(imports: dict[str, set[str]]) -> set[str]:
    res: set[str] = set().union(*imports.values())
    return res
