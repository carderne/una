import shutil
import tomllib
from pathlib import Path
from typing import Any, Literal, TypeAlias

PYPROJ = "pyproject.toml"
EXTRA_PYPROJ = Path("_extra_pyproj")
ROOT_PYPROJ_SUBDIR = Path("_root")


def load_conf(path: Path) -> dict[str, Any]:
    with (path / PYPROJ).open("rb") as fp:
        return tomllib.load(fp)


Style: TypeAlias = Literal["packages", "modules"]


def get_workspace_style(root_path: Path) -> Style:
    """
    Get the root workspace style

    Param `path` should be the path to the ap/project,
    NOT to the root workspace.
    """
    # In builds that do src -> sdist -> wheel, the root pyproject.toml file will
    # have been copied into the sdist so available for the wheel build.
    # Here we check for both in order.
    extra_root_path = EXTRA_PYPROJ / ROOT_PYPROJ_SUBDIR
    if (root_path / PYPROJ).exists():
        use_root_path = root_path
    elif (extra_root_path / PYPROJ).exists():
        use_root_path = extra_root_path
    else:
        raise ValueError("No root pyproject to determine workspace style")
    root_conf = load_conf(use_root_path)
    try:
        style: Style = root_conf["tool"]["una"]["style"]
        return style
    except KeyError as e:
        raise KeyError(
            "Root workspace pyproject.toml needs '[tool.una]' with style specified"
        ) from e


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
