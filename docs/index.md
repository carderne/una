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

Una allows two directory structures or styles:

- **Packages:** The default style, where each lib or app is a package with its own pyproject.toml (much like Rust's workspaces).
- **Modules**: A more novel approach with just a single pyproject.toml, inspired by [python-polylith](https://github.com/DavidVujic/python-polylith).

Within this context, we use the following words frequently:

- `lib`: a module or package that will be imported but not run.
- `app`: a module or package that will be run but never imported.
- `project`: a package with no code but only dependencies (only used in the Modules style).

Currently it works with the following build backends, but more will follow:

- [Hatch](https://hatch.pypa.io) (used by default and and in all documentation)
- [PDM](https://pdm-project.org/)

All instructions and examples use Rye for local development, but there is nothing inherently Rye-specific about the tool.

## Examples
You can see examples for each of the two styles here:

- [una-example-packages](https://github.com/carderne/una-example-packages)
- [una-example-modules](https://github.com/carderne/una-example-modules)
