import shutil
import tomllib
from pathlib import Path
from typing import Any

PYPROJ = "pyproject.toml"
EXTRA_PYPROJ = Path("_extra_pyproj")


def load_conf(path: Path) -> dict[str, Any]:
    with (path / PYPROJ).open("rb") as fp:
        return tomllib.load(fp)


def copy_file(src: Path, dst: Path) -> Path:
    dst.parents[0].mkdir(parents=True, exist_ok=True)
    return shutil.copyfile(src, dst)


def copy_tree(src: Path, dst: Path) -> Path:
    ignore = shutil.ignore_patterns(
        "*.pyc",
        "__pycache__",
        ".venv",
        "__pypackages__",
        ".mypy_cache",
        ".pytest_cache",
        "node_modules",
        ".git",
    )

    res: Path = shutil.copytree(  # return might not actually be a Path
        src,
        dst,
        ignore=ignore,
        dirs_exist_ok=True,
    )
    return Path(res)
