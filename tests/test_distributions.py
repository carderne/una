"""Code from https://github.com/DavidVujic/python-polylith"""

# pyright: reportPrivateUsage=false
import importlib.metadata

from una import distributions


class FakeDist:
    def __init__(self, name: str, data: str):
        self.data = data
        self.metadata = {"name": name}

    def read_text(self, *_: object) -> str:
        return self.data


def test_distribution_packages_parse_contents_of_top_level_txt():
    dists = [FakeDist("python-jose", "jose\njose/backends\n")]
    res = distributions._distributions_packages(dists)  # type: ignore[reportArgumentType]
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
        assert k == distributions._parse_sub_package_name(v)


def test_distribution_sub_packages():
    dists = list(importlib.metadata.distributions())
    res = distributions._distributions_sub_packages(dists)
    expected_dist = "typer"
    expected_sub_package = "typing-extensions"
    assert res.get(expected_dist) is not None
    assert expected_sub_package in res[expected_dist]


def test_parse_one_key_one_value_alias():
    res = distributions._parse_alias(["opencv-python=cv2"])
    assert res["opencv-python"] == ["cv2"]
    assert len(res.keys()) == 1


def test_parse_one_key_many_values_alias():
    res = distributions._parse_alias(["matplotlib=matplotlib, mpl_toolkits"])
    assert res["matplotlib"] == ["matplotlib", "mpl_toolkits"]
    assert len(res.keys()) == 1


def test_parse_many_keys_many_values_alias():
    res = distributions._parse_alias(["matplotlib=matplotlib, mpl_toolkits", "opencv-python=cv2"])
    assert res["matplotlib"] == ["matplotlib", "mpl_toolkits"]
    assert res["opencv-python"] == ["cv2"]
    assert len(res.keys()) == 2


def test_pick_alias_by_key():
    aliases = {"opencv-python": ["cv2"]}
    keys = {"one", "two", "opencv-python", "three"}
    res = distributions._pick_alias(aliases, keys)
    assert res == {"cv2"}


def test_pick_aliases_by_keys():
    aliases = {"opencv-python": ["cv2"], "matplotlib": ["mpl_toolkits", "matplotlib"]}
    keys = {"one", "two", "opencv-python", "matplotlib", "three"}
    res = distributions._pick_alias(aliases, keys)
    assert res == {"cv2", "mpl_toolkits", "matplotlib"}


def test_pick_empty_alias_by_keys():
    aliases: dict[str, list[str]] = {}
    keys = {"one", "two", "opencv-python", "matplotlib", "three"}
    res = distributions._pick_alias(aliases, keys)
    assert res == set()
