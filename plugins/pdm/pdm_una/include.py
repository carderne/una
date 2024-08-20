from pathlib import Path

from pdm.backend.hooks import Context

from pdm_una import util


def force_include(context: Context) -> None:
    """
    Force-include all needed internal monorepo dependencies.
    """
    print("una: Injecting internal dependencies")
    context.ensure_build_dir()

    build_dir = context.build_dir

    # load the config for this app/project
    path = Path(context.root)
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
    via_sdist = (util.EXTRA_PYPROJ / util.ROOT_PYPROJ_SUBDIR / util.PYPROJ).exists()
    if via_sdist:
        # nothing to do as everything should already be included in sdist...
        return

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
    util.copy_file(
        root_path / util.PYPROJ,
        build_dir / util.EXTRA_PYPROJ / util.ROOT_PYPROJ_SUBDIR / util.PYPROJ,
    )
    for src_str, dst_str in int_deps.items():
        src = Path(src_str)
        destination = build_dir / dst_str
        util.copy_tree(src, destination)
        if style == "packages":
            # need these so src->sdist->wheel builds can access them for external deps
            util.copy_file(
                src.parents[1] / util.PYPROJ,
                build_dir / util.EXTRA_PYPROJ / src.name / util.PYPROJ,
            )
