from pathlib import Path

from una import defaults
from una.types import Proj


def pick_lock_file(project: Proj) -> Path | None:
    lock = Path(project.path / defaults.lock_file)
    if not lock.exists():
        return None
    return lock


def parse_name(row: str) -> str:
    parts = str.split(row, "==")
    return parts[0]


def parse_version(row: str) -> str:
    parts = str.split(row, "==")[1]
    res = str.split(parts, " ")
    return res[0]


def extract_lib_names_from_txt(path: Path) -> dict[str, str]:
    with open(path) as f:
        data = f.readlines()
    rows = (str.strip(line) for line in data)
    filtered = (row for row in rows if row and not row.startswith(("#", "-")))
    return {parse_name(row): parse_version(row) for row in filtered}


def extract_libs(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    try:
        return extract_lib_names_from_txt(path)
    except (IndexError, KeyError, ValueError) as e:
        raise ValueError(f"Failed reading {path}: {repr(e)}") from e
