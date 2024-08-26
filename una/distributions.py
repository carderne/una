"""Code from https://github.com/DavidVujic/python-polylith"""

import importlib.metadata
import re
from functools import lru_cache, reduce
from importlib.metadata import Distribution
from typing import cast

from una.types import ExtDep

SUB_DEP_SEPARATORS = r"[\s!=;><\^~]"


def collect_deps(deps: list[ExtDep], library_alias: list[str]) -> set[str]:
    """
    Collect known aliases (packages) for third-party libraries.

    When the library origin is not from a lock-file:
    collect sub-dependencies and distribution top-namespace for each library,
    and append to the result.
    """
    third_party_libs = _extract_library_names(deps)
    dists = _get_distributions()
    dist_packages = _distributions_packages(dists)
    custom_aliases = _parse_alias(library_alias)
    sub_deps = _distributions_sub_packages(dists)
    a = _pick_alias(dist_packages, third_party_libs)
    b = _pick_alias(custom_aliases, third_party_libs)
    c = _pick_alias(_KNOWN_ALIASES, third_party_libs)
    d = _pick_alias(sub_deps, third_party_libs)
    e = _get_packages_distributions(third_party_libs)
    return third_party_libs.union(a, b, c, d, e)


def _extract_extras(name: str) -> set[str]:
    chars = ["[", "]"]
    replacement = ","
    res = reduce(lambda acc, char: str.replace(acc, char, replacement), chars, name)
    parts = str.split(res, replacement)
    return {str.strip(p) for p in parts if p}


def _extract_library_names(deps: list[ExtDep]) -> set[str]:
    names = {k.name for k in deps}
    with_extras = [_extract_extras(n) for n in names]
    res: set[str] = set().union(*with_extras)
    return res


def _parse_sub_package_name(dependency: str) -> str:
    parts = re.split(SUB_DEP_SEPARATORS, dependency)
    return str(parts[0])


def _dist_subpackages(dist: Distribution) -> dict[str, list[str]]:
    name = dist.metadata["name"]
    dependencies = importlib.metadata.requires(name) or []
    parsed_package_names = list({_parse_sub_package_name(d) for d in dependencies})
    return {name: parsed_package_names} if dependencies else {}


def _map_sub_packages(acc: dict[str, list[str]], dist: Distribution) -> dict[str, list[str]]:
    return {**acc, **_dist_subpackages(dist)}


def _parsed_top_level_namespace(namespaces: list[str]) -> list[str]:
    return [str.replace(ns, "/", ".") for ns in namespaces]


def _top_level_packages(dist: Distribution) -> list[str]:
    top_level = dist.read_text("top_level.txt")
    namespaces = str.split(top_level or "")
    return _parsed_top_level_namespace(namespaces)


def _mapped_packages(dist: Distribution) -> dict[str, list[str]]:
    packages = _top_level_packages(dist)
    name = dist.metadata["name"]
    return {name: packages} if packages else {}


def _map_packages(acc: dict[str, list[str]], dist: Distribution) -> dict[str, list[str]]:
    return {**acc, **_mapped_packages(dist)}


def _distributions_packages(dists: list[Distribution]) -> dict[str, list[str]]:
    """Return a mapping of top-level packages to their distributions."""
    return reduce(_map_packages, dists, {})


def _distributions_sub_packages(dists: list[Distribution]) -> dict[str, list[str]]:
    """Return the dependencies of each distribution."""
    init: dict[str, list[str]] = {}
    return reduce(_map_sub_packages, dists, init)


@lru_cache
def _get_distributions() -> list[Distribution]:
    return list(importlib.metadata.distributions())


def _get_packages_distributions(project_dependencies: set[str]) -> set[str]:
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


def _to_key_with_values(acc: dict[str, list[str]], alias: str) -> dict[str, list[str]]:
    k, v = str.split(alias, "=")
    values = [str.strip(val) for val in str.split(v, ",")]
    return {**acc, **{k: values}}


def _parse_alias(aliases: list[str]) -> dict[str, list[str]]:
    """Parse a list of aliases defined as key=value(s) into a dictionary"""
    return reduce(_to_key_with_values, aliases, {})


def _pick_alias(aliases: dict[str, list[str]], keys: set[str]) -> set[str]:
    matrix = [v for k, v in aliases.items() if k in keys]
    flattened = sum(matrix, cast(list[str], []))
    return set(flattened)


_KNOWN_ALIASES = {
    "beautifulsoup4": ["bs4"],
    "pillow": ["PIL"],
    "scikit-learn": ["sklearn"],
    "scikit-image": ["skimage"],
    "opencv-python": ["cv2"],
    "python-ffmpeg": ["ffmpeg"],
    "pycryptodome": ["Crypto"],
    "pycryptodomex": ["Cryptodome"],
    "pyserial": ["serial"],
    "python-multipart": ["multipart"],
    "pyusb": ["usb"],
    "pyyaml": ["yaml"],
}
