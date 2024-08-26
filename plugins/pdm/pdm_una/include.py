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

    # load the config for this package
    path = Path(context.root)
    conf = util.load_conf(path)
    name: str = conf["project"]["name"]

    try:
        int_deps: dict[str, str] = conf["tool"]["una"]["deps"]
    except KeyError as e:
        raise KeyError(f"Package '{name}' is missing '[tool.una.deps]' in pyproject.toml") from e

    if not int_deps:
        # this is fine, the package doesn't import anything internally
        return

    via_sdist = Path("PKG-INFO").exists()
    if via_sdist:
        # nothing to do as everything should already be included in sdist...
        return

    # make sure all int_deps exist
    found = [Path(k) for k in int_deps if (path / k).exists()]
    missing = set(int_deps) - set(str(p) for p in found)
    if len(missing) > 0:
        missing_str = ", ".join(missing)
        raise ValueError(f"Could not find these paths: {missing_str}")

    for src_str, dst_str in int_deps.items():
        src = Path(src_str)
        destination = build_dir / dst_str
        util.copy_tree(src, destination)
        # need these so src->sdist->wheel builds can access them for external deps
        util.copy_file(
            src.parents[1] / util.PYPROJ,
            build_dir / util.EXTRA_PYPROJ / src.name / util.PYPROJ,
        )
