from pathlib import Path
from typing import Any

from hatchling.builders.config import BuilderConfig
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from hatchling.plugin import hookimpl

from hatch_una import util


class UnaBuildHook(BuildHookInterface[BuilderConfig]):
    """
    Force-include all needed internal monorepo dependencies.
    """

    PLUGIN_NAME = "una-build"

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        print("una: Injecting internal dependencies")

        # load the config for this app/project
        path = Path(self.root)
        conf = util.load_conf(path)
        name: str = conf["project"]["name"]

        try:
            int_deps: dict[str, str] = conf["tool"]["una"]["libs"]
        except KeyError as e:
            raise KeyError(
                f"App/project '{name}' is missing '[tool.una.libs]' in pyproject.toml"
            ) from e

        # need to determine workspace style (packages or modules)
        # as packages style needs dependencies' pyproject.tomls to be included
        # so that they're available in src -> sdist -> wheel builds
        root_path = path.parents[1]
        style = util.get_workspace_style(root_path)

        if not int_deps:
            if style == "packages":
                # this is fine, the app doesn't import anything internally
                return
            else:
                # this is an empty project, useless and accidental
                raise ValueError(f"Project '{name}' has no dependencies")

        # make sure all int_deps exist
        found = [Path(k) for k in int_deps if (path / k).exists()]
        missing = set(int_deps) - set(str(p) for p in found)
        if len(missing) > 0:
            missing_str = ", ".join(missing)
            raise ValueError(f"Could not find these paths: {missing_str}")

        # need to add the root workspace pyproject.toml so that in src -> sdist -> wheel builds,
        # we can still determine the style (for packages style)
        add_root_pyproj = {
            str(root_path / util.PYPROJ): str(
                util.EXTRA_PYPROJ / util.ROOT_PYPROJ_SUBDIR / util.PYPROJ
            )
        }
        if style == "packages":
            add_packages_pyproj = {
                str(f.parents[1] / util.PYPROJ): str(util.EXTRA_PYPROJ / f.name / util.PYPROJ)
                for f in found
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
