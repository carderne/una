from pathlib import Path
from typing import Any

from hatchling.builders.config import BuilderConfig
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from hatchling.plugin import hookimpl

from hatch_una import util


class UnaBuildHook(BuildHookInterface[BuilderConfig]):
    PLUGIN_NAME = "una-build"

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        print("una: Injecting internal dependencies")
        root = Path(self.root)
        conf = util.load_conf(root)

        int_deps: dict[str, str] = conf["tool"]["una"]["libs"]
        found = [Path(k) for k in int_deps if (root / k).exists()]
        if not int_deps or not found:
            # should I raise here?
            return

        add_pyproj = {str(f.parents[1] / util.PYPROJ): str(util.EXTRA_PYPROJ / f.name / util.PYPROJ) for f in found}
        build_data["force_include"] = {**build_data["force_include"], **int_deps, **add_pyproj}


@hookimpl
def hatch_register_build_hook() -> type[UnaBuildHook]:
    return UnaBuildHook
