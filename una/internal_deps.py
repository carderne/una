from pathlib import Path

from una import check, files
from una.types import Include, IntDeps, OrgImports, Proj


def get_int_dep_imports(root: Path, ns: str, libs: set[str]) -> OrgImports:
    comp_paths = files.collect_libs_paths(root, ns, libs)
    int_dep_imports_in_libs = check.extract_int_deps(comp_paths, ns)
    return OrgImports(
        libs=check.with_unknown_libs(root, ns, int_dep_imports_in_libs),
    )


def get_projects_data(root: Path, ns: str) -> list[Proj]:
    lib_names = files.get_libs(root, ns)
    return _get_int_deps_in_projects(root, lib_names, ns)


def filtered_projects_data(projects: list[Proj]) -> list[Proj]:
    return [p for p in projects if Path.cwd().name in p.path.as_posix()]


def _get_matching_int_deps(paths: list[Path], int_deps: list[str], namespace: str) -> list[str]:
    paths_in_namespace = [p.name for p in paths if p.parent.name == namespace]
    res = set(int_deps).intersection(paths_in_namespace)
    return sorted(list(res))


def _get_project_int_deps(
    project_packages: list[Include],
    libs_paths: list[str],
    namespace: str,
    self_name: str,
) -> IntDeps:
    paths = files.parse_package_paths(project_packages)
    libs_in_project = _get_matching_int_deps(paths, libs_paths, namespace)
    libs_in_project.append(self_name)
    return IntDeps(libs=libs_in_project)


def _get_int_deps_in_projects(root: Path, libs_paths: list[str], namespace: str) -> list[Proj]:
    packages = files.get_projects(root)
    res = [
        Proj(
            name=p.name,
            packages=p.packages,
            path=p.path,
            ext_deps=p.ext_deps,
            int_deps=_get_project_int_deps(
                p.packages,
                libs_paths,
                namespace,
                p.name,
            ),
        )
        for p in packages
    ]
    return res
