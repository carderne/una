from pathlib import Path

from una import config, sync
from una.types import Diff, Include, OrgImports, Style


def test_int_dep_to_pyproject_package():
    ns = "unit_test"
    int_dep = "greet"
    root = "../../libs"
    expected_proj = Include(src=f"{root}/{ns}/{int_dep}", dst=f"{ns}/{int_dep}")
    style = Style.modules
    res_proj = sync.to_package(ns, int_dep, root, style)
    assert res_proj == expected_proj


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
    res = sync.to_packages(ns, diff)
    assert res == expected


packages = [
    Include(src="apps/hello/first", dst="hello/first"),
    Include(src="libs/hello/second", dst="hello/second"),
    Include(src="libs/hello/third", dst="hello/third"),
]
expected_hatch_packages = {
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
[tool.una.libs]
"apps/hello/first" = "hello/first"
"""
    conf = config.load_conf_from_str(pyproj)
    updated = str(sync.generate_updated_project(conf, packages[1:]))
    res = config.load_conf_from_str(updated).tool.una.libs
    assert res == expected_hatch_packages


def test_generate_updated_hatch_project_with_missing_int_dep_config():
    pyproj = f"""
{BASE_PYPROJECT}
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
[tool.hatch.build]
    """
    conf = config.load_conf_from_str(pyproj)
    updated = str(sync.generate_updated_project(conf, packages))
    res = config.load_conf_from_str(updated).tool.una.libs
    assert res == expected_hatch_packages
