# Una

<div align="center">
  <img src="assets/logo.svg" width="100">
  <p>Easy monorepos with Python</p>
</div>

----
<div align="center">

<a href="https://pypi.org/project/una/">
<img alt="pypi" src="https://img.shields.io/pypi/v/una.svg?logo=pypi&label=PyPI&logoColor=gold">
</a>
<a href="https://una.rdrn.me/">
<img alt="docs" src="https://img.shields.io/badge/Docs-gray?logo=materialformkdocs&logoColor=white">
</a>
<a href="https://github.com/carderne/una">
<img alt="GitHub" src="https://img.shields.io/badge/GitHub-una-blue?logo=github">
</a>

</div>

Una is a tool to make Python monorepos easier. It is a CLI tool and a build plugin that does the following things:

1. Enable builds of individual apps or projects within a monorepo.
2. Ensure that internal and external dependencies are correctly specified.

Una doesn't try to replicate a full build system such as [Bazel](https://bazel.build/) or [Pants](https://www.pantsbuild.org/). It just makes it possible to have a simple monorepo with interdependencies.

Una works much like a Rust workspace, with each package having its own pyproject.toml. In general, packages should either be libraries (imported but not run) or apps (run but never imported), but Una will not enforce this.

Currently it works with the following build backends, but more will follow:

- [Hatch](https://hatch.pypa.io) (used by default and and in all documentation)
- [PDM](https://pdm-project.org/)

All instructions and examples use Rye for local development, but there is nothing inherently Rye-specific about the tool.

## Examples
You can see an example repo here:

- [una-example](https://github.com/carderne/una-example-packages)
