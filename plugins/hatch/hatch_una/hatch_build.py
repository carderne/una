import tomllib
from pathlib import Path
from typing import Any

from hatchling.builders.config import BuilderConfig
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from hatchling.plugin import hookimpl


class BuildConfig(BuilderConfig):
    pass


class UnaHook(BuildHookInterface[BuildConfig]):
    PLUGIN_NAME = "una-build"

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        print("una: Injecting internal dependencies")
        root = Path(self.root)
        with (root / "pyproject.toml").open("rb") as fp:
            conf = tomllib.load(fp)

        int_deps: dict[str, str] = conf["tool"]["una"]["libs"]
        found = {k: v for k, v in int_deps.items() if (root / k).exists()}
        if not int_deps or not found:
            return
        build_data["force_include"] = {**build_data["force_include"], **int_deps}


@hookimpl
def hatch_register_build_hook():
    return UnaHook
