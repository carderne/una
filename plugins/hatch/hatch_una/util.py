import tomllib
from pathlib import Path
from typing import Any, Literal, TypeAlias

PYPROJ = "pyproject.toml"
EXTRA_PYPROJ = Path("extra_pyproj")


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
    extra_root_path = EXTRA_PYPROJ / "root"
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
