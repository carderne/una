# Una

<div align="center">
  <img src="https://raw.githubusercontent.com/carderne/una/main/docs/assets/logo.svg" alt="Una logo" width="100" role="img">
  <p>Easy monorepos with Python and uv</p>
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

**This is a new project that is still evolving. I'm very open to ideas, suggestions and feedback. Please open an [issue](https://github.com/carderne/una/issues/new) with your comments.**

Una is a tool to build and productionise Python monorepos with [uv](https://docs.astral.sh/uv/).

uv has [Workspaces](https://docs.astral.sh/uv/concepts/workspaces/), but no ability to _build_ them.
This means if you have dependencies between packages in your workspace, there's no good way to distribute or productionise the end result.

Una solves this.
No additional configuration is needed: if you have a functional uv Workspace, just add Una.
It consists of the following two things:

1. A CLI to ensure that all imports are correctly specified as dependencies.
2. A build plugin that enables production builds of individual apps within a monorepo by injecting local dependencies and transitive third-party dependencies.

Una doesn't try to replicate a full build system such as [Bazel](https://bazel.build/) or
[Pants](https://www.pantsbuild.org/).
It just makes it possible to have a simple monorepo with interdependencies.

Una works much like a Rust workspace, with each package having its own pyproject.toml.
In general, packages should either be libraries (imported but not run) or apps (run but never imported), but Una will not enforce this.

It only works with the [Hatch](https://hatch.pypa.io) build backend.

## Examples
You can see an example repo here:

- [una-example](https://github.com/carderne/una-example)

## Quickstart
This will give you a quick view of how this all works.

First install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

And start your workspace:
```bash
uv init unarepo   # choose another name if you prefer
cd unarepo
git init
uv add --dev una
```

Then setup the Una workspace. This will generate a structure and an example lib and app.
```bash
uv run una create workspace
rm -rf src
uv sync
```

Have a look at what's been generated:
```bash
tree
```

Have a look at the generated `__init__.py` files in the `apps/printer` and `libs/greeter` packages.
An external dependency ([cowsay-python](https://pypi.org/project/cowsay-python/)) has also been added to the latter's `pyproject.toml`.

The magic of Una then comes in to resolve the graph of direct and transitive dependencies, which looks like this:
```elm
printer --> greeter --> cowsay-python
```

You can do this by running the following:
```bash
# this checks all imports and ensures they are added to
# project.dependencies and tool.uv.sources in the each pyproject.toml
uv run una sync
```

Have a look at what happened:
```bash
tail apps/printer/pyproject.toml
```

It added `greeter` as an internal dependency to `printer`.
It didn't add `cowsay-python`, as transitive external dependencies are only resolved at build-time.

Now you can build your app. Note that you **must** specify the `--wheel` parameter. Una doesn't currently work for builds that do source -> sdist -> wheel, as these break some things with uv virtual envs.
```bash
uvx --from build pyproject-build --installer=uv \
    --outdir=dist --wheel apps/printer
# this will inject the cowsay-python external dependency
```

And see the result:
```bash
ls dist/
```

And you can do whatever you want with that wheel!
What about stick it in a Dockerfile, have you ever seen such a simple one?
```Dockerfile
FROM python
COPY dist dist
RUN pip install dist/*.whl
```

And run it:
```bash
docker build --tag unarepo-printer .
docker run --rm -it unarepo-printer python -c 'from unarepo.printer import run; run()'
```

## Installation
The CLI tool isn't strictly necessary, as all the stuff that lets the monorepo builds work is in the separate (and tiny) [hatch-una](plugins/hatch) package.
But you will likely struggle to manage your monorepo without the tool!

So you may as well install it:
```bash
uv add --dev una
```

As for the build-time `hatch-una`, it will automatically be installed by build tools when it spots this in your `pyproject.toml` (this will be configured automatically by the CLI):
```toml
[build-system]
requires = ["hatchling", "hatch-una"]
build-backend = "hatchling.build"
```

## Usage
The CLI has a few commands and options, have a look:
```bash
uv run una --help

 Usage: una [OPTIONS] COMMAND [ARGS]...

╭─ Options ─────────────────────────────────────────────╮
│ --help          Show this message and exit.           │
╰───────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────╮
│ create   Commands for creating workspace and packages.│
│ sync     Update packages with missing dependencies.   │
╰───────────────────────────────────────────────────────╯
```

## Documentation

Read more at [the official documentation](https://una.rdrn.me/).

It covers additional things like:
- [type-checking](https://una.rdrn.me/types-tests/), testing, editor integration
- and more!

## Contributing
See the instructions at the [official documentation](https://una.rdrn.me/contributing/).

Very briefly, local development is with uv:
```bash
uv sync
make all  # will fmt, lint, typecheck and test
```

Then open a PR.

## License
Una is distributed under the terms of the MIT license.
Some code is from the [python-polylith](https://github.com/DavidVujic/python-polylith) project (c) 2022 David Vujic
