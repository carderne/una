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
        monkeypatch.setattr(
            config,
            "load_conf",
            lambda _: config.load_conf_from_str(BASE_PYPROJECT),  # type: ignore[reportUnknownArgumentType]
        )

    return patch


NAMESPACE = "unittest"
HATCH_TOML = f"""
{BASE_PYPROJECT}
[tool.una.deps]
"../../apps/unittest/one" = "unittest/one"
"../../libs/unittest/two" = "unittest/two"
"""

expected_packages = [
    Include(src="../../apps/unittest/one", dst="unittest/one"),
    Include(src="../../libs/unittest/two", dst="unittest/two"),
]


def test_get_hatch_package_includes():
    conf = config.load_conf_from_str(HATCH_TOML)
    res = config.get_project_package_includes(NAMESPACE, conf)
    assert res == expected_packages
