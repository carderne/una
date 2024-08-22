from pathlib import Path

from una import defaults
from una.types import Proj


def pick_lock_file(project: Proj) -> Path | None:
    lock = Path(project.path / defaults.LOCK_FILE)
    if not lock.exists():
        return None
    return lock


def extract_libs(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    try:
        return _extract_lib_names_from_txt(path)
    except (IndexError, KeyError, ValueError) as e:
        raise ValueError(f"Failed reading {path}: {repr(e)}") from e


def _parse_name(row: str) -> str:
    parts = str.split(row, "==")
    return parts[0]


def _parse_version(row: str) -> str:
    parts = str.split(row, "==")[1]
    res = str.split(parts, " ")
    return res[0]


def _extract_lib_names_from_txt(path: Path) -> dict[str, str]:
    with open(path) as f:
        data = f.readlines()
    rows = (str.strip(line) for line in data)
    filtered = (row for row in rows if row and not row.startswith(("#", "-")))
    return {_parse_name(row): _parse_version(row) for row in filtered}
