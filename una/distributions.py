import importlib.metadata
import re
from functools import lru_cache, reduce
from importlib.metadata import Distribution

from una import alias
from una.types import ExtDeps

SUB_DEP_SEPARATORS = r"[\s!=;><\^~]"


def extract_extras(name: str) -> set[str]:
    chars = ["[", "]"]
    replacement = ","
    res = reduce(lambda acc, char: str.replace(acc, char, replacement), chars, name)
    parts = str.split(res, replacement)
    return {str.strip(p) for p in parts if p}


def extract_library_names(deps: ExtDeps) -> set[str]:
    names = {k for k in deps.items}
    with_extras = [extract_extras(n) for n in names]
    res: set[str] = set().union(*with_extras)
    return res


def known_aliases_and_sub_dependencies(deps: ExtDeps, library_alias: list[str]) -> set[str]:
    """Collect known aliases (packages) for third-party libraries.
    When the library origin is not from a lock-file:
    collect sub-dependencies and distribution top-namespace for each library, and append to the result.
    """
    lock_file = any(str.endswith(deps.source, s) for s in {".lock", ".txt"})
    third_party_libs = extract_library_names(deps)
    dists = get_distributions()
    dist_packages = distributions_packages(dists)
    custom_aliases = alias.parse(library_alias)
    sub_deps = distributions_sub_packages(dists) if not lock_file else {}
    a = alias.pick(dist_packages, third_party_libs)
    b = alias.pick(custom_aliases, third_party_libs)
    c = alias.pick(alias.KNOWN_ALIASES, third_party_libs)
    d = alias.pick(sub_deps, third_party_libs)
    e = get_packages_distributions(third_party_libs)
    return third_party_libs.union(a, b, c, d, e)


def parse_sub_package_name(dependency: str) -> str:
    parts = re.split(SUB_DEP_SEPARATORS, dependency)
    return str(parts[0])


def dist_subpackages(dist: Distribution) -> dict[str, list[str]]:
    name = dist.metadata["name"]
    dependencies = importlib.metadata.requires(name) or []
    parsed_package_names = list({parse_sub_package_name(d) for d in dependencies})
    return {name: parsed_package_names} if dependencies else {}


def map_sub_packages(acc: dict[str, list[str]], dist: Distribution) -> dict[str, list[str]]:
    return {**acc, **dist_subpackages(dist)}


def parsed_top_level_namespace(namespaces: list[str]) -> list[str]:
    return [str.replace(ns, "/", ".") for ns in namespaces]


def top_level_packages(dist: Distribution) -> list[str]:
    top_level = dist.read_text("top_level.txt")
    namespaces = str.split(top_level or "")
    return parsed_top_level_namespace(namespaces)


def mapped_packages(dist: Distribution) -> dict[str, list[str]]:
    packages = top_level_packages(dist)
    name = dist.metadata["name"]
    return {name: packages} if packages else {}


def map_packages(acc: dict[str, list[str]], dist: Distribution) -> dict[str, list[str]]:
    return {**acc, **mapped_packages(dist)}


def distributions_packages(dists: list[Distribution]) -> dict[str, list[str]]:
    """Return a mapping of top-level packages to their distributions."""
    return reduce(map_packages, dists, {})


def distributions_sub_packages(dists: list[Distribution]) -> dict[str, list[str]]:
    """Return the dependencies of each distribution."""
    init: dict[str, list[str]] = {}
    return reduce(map_sub_packages, dists, init)


@lru_cache
def get_distributions() -> list[Distribution]:
    return list(importlib.metadata.distributions())


def get_packages_distributions(project_dependencies: set[str]) -> set[str]:
    """Return the mapped top namespace from an import
    Example:
    A third-party library, such as opentelemetry-instrumentation-fastapi.
    The return value would be the mapped top namespace: opentelemetry
    Note: available for Python >= 3.10
    """
    # added in Python 3.10
    dists = importlib.metadata.packages_distributions()
    common = {k for k, v in dists.items() if project_dependencies.intersection(set(v))}
    return common.difference(project_dependencies)
