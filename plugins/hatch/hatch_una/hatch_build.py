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
        path = Path(self.root)
        conf = util.load_conf(path)

        root_path = path.parents[1]
        extra_root_path = util.EXTRA_PYPROJ / "root"
        if (root_path / util.PYPROJ).exists():
            use_root_path = root_path
        elif (extra_root_path / util.PYPROJ).exists():
            use_root_path = extra_root_path
        else:
            raise ValueError("No root pyproject to determine workspace style")
        root_conf = util.load_conf(use_root_path)
        style: str = root_conf["tool"]["una"]["style"]

        int_deps: dict[str, str] = conf["tool"]["una"]["libs"]
        found = [Path(k) for k in int_deps if (path / k).exists()]
        if not int_deps or not found:
            # should I raise here?
            return

        add_root_pyproj = {str(root_path / util.PYPROJ): str(util.EXTRA_PYPROJ / "root" / util.PYPROJ)}
        if style == "packages":
            add_packages_pyproj = {
                str(f.parents[1] / util.PYPROJ): str(util.EXTRA_PYPROJ / f.name / util.PYPROJ) for f in found
            }
        else:
            add_packages_pyproj = {}

        build_data["force_include"] = {
            **build_data["force_include"],
            **int_deps,
            **add_root_pyproj,
            **add_packages_pyproj,
        }


@hookimpl
def hatch_register_build_hook() -> type[UnaBuildHook]:
    return UnaBuildHook
