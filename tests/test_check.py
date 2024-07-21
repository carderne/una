from pathlib import Path

from una import check
from una.types import ExtDeps, Options, Proj


def test_collect_known_aliases_and_sub_dependencies():
    fake_project_data = Proj(
        name="",
        packages=[],
        path=Path(),
        ext_deps=ExtDeps(
            items={"typer": "1", "hello-world-library": "2"},
            source="unit-test",
        ),
    )
    fake_options = Options(alias=["hello-world-library=hello"])
    res = check.collect_known_aliases(fake_project_data, fake_options)
    assert "typer" in res
    assert "typing-extensions" in res
    assert "hello" in res
