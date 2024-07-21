import importlib.metadata

from una import distributions
from una.types import ExtDeps


class FakeDist:
    def __init__(self, name: str, data: str):
        self.data = data
        self.metadata = {"name": name}

    def read_text(self, *args: object) -> str:
        return self.data


def test_distribution_packages_parse_contents_of_top_level_txt():
    dists = [FakeDist("python-jose", "jose\njose/backends\n")]
    res = distributions.distributions_packages(dists)  # type: ignore[reportArgumentType]
    expected_dist = "python-jose"
    expected_packages = ["jose", "jose.backends"]
    assert res.get(expected_dist) is not None
    assert res[expected_dist] == expected_packages


def test_parse_package_name_from_dist_requires():
    expected = {
        "greenlet": "greenlet !=0.4.17",
        "mysqlclient": "mysqlclient >=1.4.0 ; extra == 'mysql'",
        "typing-extensions": "typing-extensions>=4.6.0",
        "pymysql": "pymysql ; extra == 'pymysql'",
        "one": "one<=0.4.17",
        "two": "two^=0.4.17",
        "three": "three~=0.4.17",
    }
    for k, v in expected.items():
        assert k == distributions.parse_sub_package_name(v)


def test_distribution_sub_packages():
    dists = list(importlib.metadata.distributions())
    res = distributions.distributions_sub_packages(dists)
    expected_dist = "typer"
    expected_sub_package = "typing-extensions"
    assert res.get(expected_dist) is not None
    assert expected_sub_package in res[expected_dist]


def test_parse_third_party_library_name():
    fake_project_deps = ExtDeps(
        items={
            "python": "^3.10",
            "fastapi": "^0.110.0",
            "uvicorn[standard]": "^0.27.1",
            "python-jose[cryptography]": "^3.3.0",
            "hello[world, something]": "^3.3.0",
        },
        source="pyproject.toml",
    )
    expected = {
        "python",
        "fastapi",
        "uvicorn",
        "standard",
        "python-jose",
        "cryptography",
        "hello",
        "world",
        "something",
    }
    res = distributions.extract_library_names(fake_project_deps)
    assert res == expected
