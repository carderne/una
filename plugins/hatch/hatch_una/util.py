import tomllib
from pathlib import Path
from typing import Any

PYPROJ = "pyproject.toml"
EXTRA_PYPROJ = Path("_extra_pyproj")


def load_conf(path: Path) -> dict[str, Any]:
    with (path / PYPROJ).open("rb") as fp:
        return tomllib.load(fp)
