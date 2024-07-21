from una import external_deps
from una.types import OrgImports


def test_calculate_diff_reports_no_diff():
    int_dep_imports = OrgImports(
        apps={"my_app": {"rich"}},
        libs={
            "one": {"rich"},
            "two": {"rich", "foo"},
            "thre": {"tomlkit"},
        },
    )
    third_party_libs = {
        "tomlkit",
        "foo",
        "requests",
        "rich",
    }
    res = external_deps.calculate_diff(int_dep_imports, third_party_libs, True)
    assert len(res) == 0


def test_calculate_diff_should_report_missing_dependency():
    expected_missing = "aws-lambda-powertools"
    int_dep_imports = OrgImports(
        apps={"my_app": {"foo"}},
        libs={
            "one": {"tomlkit"},
            "two": {"tomlkit", expected_missing, "rich"},
            "three": {"rich"},
        },
    )
    third_party_libs = {
        "tomlkit",
        "foo",
        "mypy-extensions",
        "rich",
    }
    res = external_deps.calculate_diff(int_dep_imports, third_party_libs, True)
    assert res == {expected_missing}


def test_calculate_diff_should_identify_close_match():
    int_dep_imports = OrgImports(
        apps={"my_app": {"foo"}},
        libs={
            "one": {"tomlkit"},
            "two": {"tomlkit", "aws_lambda_powertools", "rich"},
            "three": {"rich", "pyyoutube"},
        },
    )
    third_party_libs = {
        "tomlkit",
        "python-youtube",
        "foo",
        "aws-lambda-powertools",
        "rich",
    }
    res = external_deps.calculate_diff(int_dep_imports, third_party_libs, True)
    assert len(res) == 0


def test_calculate_diff_should_identify_close_match_case_insensitive():
    int_dep_imports = OrgImports(
        apps={"my_app": set()},
        libs={"one": {"PIL"}},
    )
    third_party_libs = {"pillow"}
    res = external_deps.calculate_diff(int_dep_imports, third_party_libs, True)
    assert len(res) == 0
