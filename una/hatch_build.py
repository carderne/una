from pathlib import Path
from typing import Any

from hatchling.builders.config import BuilderConfig
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from hatchling.plugin import hookimpl

from una import config


class BuildConfig(BuilderConfig):
    pass


class UnaHook(BuildHookInterface[BuildConfig]):
    PLUGIN_NAME = "una-build"

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        root = self.root
        conf = config.load_conf(root)
        int_deps = conf.tool.una.libs
        found = {k: v for k, v in int_deps.items() if Path(f"{root}/{k}").exists()}
        if not int_deps or not found:
            return
        build_data["force_include"] = int_deps


@hookimpl
def hatch_register_build_hook():
    return UnaHook
