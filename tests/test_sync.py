# pyright: reportPrivateUsage=false
from pathlib import Path

from una import config, sync
from una.types import Diff, Include, OrgImports


def test_int_deps_to_pyproject_packages():
    ns = "unit_test"
    app_name = "hello"
    lib_name = "world"
    expected = [
        Include(src=f"../../apps/{app_name}/{ns}/{app_name}", dst=f"{ns}/{app_name}"),
        Include(src=f"../../libs/{lib_name}/{ns}/{lib_name}", dst=f"{ns}/{lib_name}"),
    ]
    diff = Diff(
        name="unit-test",
        path=Path.cwd(),
        apps={app_name},
        libs={lib_name},
        int_dep_imports=OrgImports(),
    )
    res = sync._to_packages(ns, diff)
    assert res == expected


INCLUDES = [
    Include(src="apps/hello/first", dst="hello/first"),
    Include(src="libs/hello/second", dst="hello/second"),
    Include(src="libs/hello/third", dst="hello/third"),
]

EXPEXTED_HATCH_PACKAGES = {
    "apps/hello/first": "hello/first",
    "libs/hello/second": "hello/second",
    "libs/hello/third": "hello/third",
}

BASE_PYPROJECT = """
[project]
name = ""
version = ""
description = ""
authors = []
dependencies = []
readme = ""
requires-python = ""
"""


def test_generate_updated_hatch_project_with_existing_una_sections():
    pyproj = f"""
{BASE_PYPROJECT}
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
[tool.hatch.build]
[tool.una.deps]
"apps/hello/first" = "hello/first"
"""
    conf = config.load_conf_from_str(pyproj)
    updated = str(sync._generate_updated_project(conf, INCLUDES[1:]))
    res = config.load_conf_from_str(updated).tool.una.deps
    assert res == EXPEXTED_HATCH_PACKAGES


def test_generate_updated_hatch_project_with_missing_int_dep_config():
    pyproj = f"""
{BASE_PYPROJECT}
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
[tool.hatch.build]
    """
    conf = config.load_conf_from_str(pyproj)
    updated = str(sync._generate_updated_project(conf, INCLUDES))
    res = config.load_conf_from_str(updated).tool.una.deps
    assert res == EXPEXTED_HATCH_PACKAGES
