from pathlib import Path

import pytest
from pytest import MonkeyPatch

from una import config
from una.types import Include

BASE_PYPROJECT = """
[project]
name = ""
version = ""
description = ""
authors = []
readme = ""
requires-python = ""
dependencies = ["fastapi~=0.109.2", "uvicorn~=0.25.0", "tomlkit"]
[tool.hatch.build]
"""


@pytest.fixture
def use_fake(monkeypatch: MonkeyPatch):
    def patch():
        monkeypatch.setattr(config, "load_conf", lambda _: config.load_conf_from_str(BASE_PYPROJECT))  # type: ignore[reportUnknownArgumentType]

    return patch


fake_path = Path.cwd()


namespace = "unittest"
hatch_toml = f"""
{BASE_PYPROJECT}
[tool.una.libs]
"../../apps/unittest/one" = "unittest/one"
"../../libs/unittest/two" = "unittest/two"
"""

pep_621_toml_deps = f"""
{BASE_PYPROJECT}
[project.optional-dependencies]
dev = ["an-optional-lib==1.2.3", "another"]
local = ["awsglue-local-dev==1.0.0"]
"""
expected_packages = [
    Include(src="../../apps/unittest/one", dst="unittest/one"),
    Include(src="../../libs/unittest/two", dst="unittest/two"),
]


def test_get_hatch_package_includes():
    conf = config.load_conf_from_str(hatch_toml)
    res = config.get_project_package_includes(namespace, conf)
    assert res == expected_packages


def test_parse_pep_621_project_dependencies():
    expected_dependencies = {
        "fastapi": "~=0.109.2",
        "uvicorn": "~=0.25.0",
        "tomlkit": "",
        "an-optional-lib": "==1.2.3",
        "another": "",
        "awsglue-local-dev": "==1.0.0",
    }
    conf = config.load_conf_from_str(pep_621_toml_deps)
    res = config.parse_project_dependencies(conf)
    assert res == expected_dependencies
