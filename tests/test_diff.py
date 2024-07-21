from pathlib import Path

from una import differ

root = Path.cwd()
ns = "my_namespace"
changed_files = [
    Path(f"libs/{ns}/a/core.py"),
    Path(f"some/other/{ns}/file.py"),
    Path(f"apps/{ns}/b/core.py"),
    Path(f"libs/{ns}/b/core.py"),
    Path(f"libs/{ns}/c/nested/subfolder/core.py"),
]


def test_get_changed_libs():
    res = differ.get_changed_libs(root, changed_files, ns)
    assert res == ["a", "b", "c"]


def test_get_changed_apps():
    res = differ.get_changed_apps(root, changed_files, ns)
    assert res == ["b"]
