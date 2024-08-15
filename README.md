# una
**Warning: this is pre-alpha and probably doesn't work at all. You'll probably just get frustrated if you even try to use it.**

una is a tool to make Python monorepos with Rye easier. It is a CLI tool and a Hatch plugin that does the following things:
1. Enable builds of individual apps or projects within a monorepo.
2. Ensure that internal and external dependencies are correctly specified.

una is inspired by [python-polylith](https://github.com/DavidVujic/python-polylith) and is based on that codebase.
But I find the [Polylith](https://polylith.gitbook.io/polylith) architecture to be quite intimidating for many, so wanted to create a lighter touch alternative that doesn't require too much re-thinking. This project has very limited ambitions and doesn't try to do everything a proper build system such as [Bazel](https://bazel.build/) or [Pants](https://www.pantsbuild.org/) does.
It just tries to make a simple monorepo build just about possible.

una allows two directory structures or styles:
- `packages`: this is the lightest-touch approach, that is just some extra build help on top of a Rye workspace.
- `modules`: a more novel approach with just a single pyproject.toml, arguably better DevX and doesn't require a Rye workspace.

Within this context, we use the following words frequently:
- `lib`: a module or package that will be imported but not run.
- `app`: a module or package that will be run but never imported.
- `project`: a package with no code but only dependencies (only used in the `modules` style)

## Quickstart
This will give you a quick view of how this all works.
A `packages` style will be used by default, as it is probably more familiar to most.

```bash
rye init my_example
cd my_example
rye add --dev una

# this will create a bunch of folders and files, have a look at them!
rye run una create workspace

# why not have a look
tree
```

The let's create some internal and external dependencies:
```bash
# add an external library to example_lib
cd libs/example_lib
rye add urllib3
cd ../..

# and then depend on example_lib from example_app
echo "import my_example.example_lib" > apps/example_app/my_example/example_app/foo.py
```

But then how do we ensure that builds of example_app will include all of the required code and dependencies?
```bash
# this checks all imports and ensures they are added to
# [tool.una.libs] in the appropriate pyproject.toml
rye run una sync

# have a look at what happened
tail apps/example_app/pyproject.toml
```

Now you can build your app:
```bash
rye build --package example_app

# and see the result
ls dist/
```

And you can do whatever you want with that wheel!
What about stick it in a Dockerfile, have you ever seen such a simple one?
```Dockerfile
FROM python
COPY dist dist
RUN pip install dist/*.whl
```

## Installation
The CLI tool isn't strictly necessary, as all the stuff that lets the monorepo builds work is in the separate (and tiny) [hatch-una](plugins/hatch) package.
But you will likely struggle to manage your monorepo without the tool!

So you may as well install it:
```bash
pip install una
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
rye run una --help

 Usage: una [OPTIONS] COMMAND [ARGS]...

╭─ Options ───────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                             │
╰─────────────────────────────────────────────────────────────────────────╯
╭─ Commands ──────────────────────────────────────────────────────────────╮
│ create   Commands for creating a workspace, apps, libs and projects.    │
│ diff     Shows changed int_deps compared to the latest git tag.         │
│ info     Info about the Una workspace.                                  │
│ sync     Update pyproject.toml with missing int_deps.                   │
╰─────────────────────────────────────────────────────────────────────────╯
```

## Type-checking, testing, editors
### Pyright
With the `packages` style (the default), you'll need to configure pyright for each package.

That is, you should add something like the config below to each `apps/*/pyproject.toml` and `libs/*/pyproject.toml`.

```toml
[tool.pyright]
venvPath = "../.."
venv = ".venv"
pythonVersion = "3.11"
strict = ["**/*.py"]
```

Once that is added, you can run `rye run pyright` in the root and it should work correctly.

With the `modules` style this is not necessary, and you can just have one root Pyright (and Pytest!).

### Pytest
You can just configure pytest as follows in the root pyproject.toml:
```toml
[tool.pytest.ini_options]
pythonpath = [
  "apps/*",
  "libs/*"
]
testpaths = [
  "apps/*",
  "libs/*",
]
addopts = ""
```

## Styles
### Style: Packages
In this setup, we use Rye's built-in workspace support. The structure will look something like this:
```bash
.
├── pyproject.toml
├── requirements.lock
├── apps
│   └── server
│       ├── pyproject.toml
│       ├── your_ns
│       │   └── server
│       │       ├── __init__.py
│       └── tests
│           └── test_server.py
└── libs
    └── mylib
        ├── pyproject.toml
        ├── your_ns
        │   └── mylib
        │       ├── __init__.py
        │       └── py.typed
        └── tests
            └── test_mylib.py
```

This means:
1. Each `app` or `lib` (collectively, internal dependencies) is it's own Python package with a `pyproject.toml`.
2. You must specify the workspace members in `tool.rye.workspace.members`.
3. Type-checking and testing should be done on a per-package level.
That is, you should run `pyright` and `pytest` from `apps/server` or `libs/mylib`, _not_ from the root.

In the example above, the only build artifact will be for `apps/server`. At build-time, una will do the following:
1. Read the list of internal dependencies (more on this shortly) and inject them into the build.
2. Read all externel requirements of those dependencies, and add them to the dependency table.

You can then use the `una` CLI tool to ensure that all internal dependencies are kept in sync. What are the key steps?
1. Use a Rye workspace:
```toml
# /pyproject.toml
[tool.rye]
managed = true
virtual = true

[tool.rye.workspace]
members = ["apps/*", "libs/*"]
```

2. Create your apps and your libs as you would, ensuring that app code is never imported.
Ensure that you choose a good namespace and always use it in your package structures (check `your_ns` in the example structure above.)
3. Add external dependencies to your libs and apps as normal.
Then, to add an internal dependency to an app, we do the following in its pyproject.toml:
```toml
# /apps/server/pyproject.toml
[build-system]
requires = ["hatchling", "hatch-una"]
build-backend = "hatchling.build"

[tool.hatch.build.hooks.una-build]
[tool.hatch.build.hooks.una-meta]
[tool.una.libs]
"../../libs/mylib/example/mylib" = "example/mylib"
```
4. Then you can run `rye build --wheel` from that package directory and una will inject everything that is needed.
Once you have your built `.whl` file, all you need in your Dockerfile is:
```Dockerfile
FROM python
COPY dist dist
RUN pip install dist/*.whl
```

### Style: Modules
This approach is inspired by [Polylith](https://davidvujic.github.io/python-polylith-docs/).
You don't use a Rye workspace (and indeed this approach will work with just Hatch), and there's only a single `pyproject.toml`.

The structure looks like this:
```bash
.
├── pyproject.toml
├── requirements.lock
├── apps
│   └── your_ns
│       └── server
│           ├── __init__.py
│           └── test_server.py
├── libs
│   └── your_ns
│       └── mylib
│           ├── __init__.py
│           ├── core.py
│           └── test_core.py
└── projects
    └── server
        └── pyproject.toml
```

The key differences are as follows:
1. `apps/` and `libs/` contain only pure Python code, structured into modules under a common namespace.
2. Tests are colocated with Python code (this will be familiar to those coming from Go or Rust).
3. Because `apps/` is just pure Python code, we need somewhere else to convert this into deployable artifacts (Docker images and the like).
So we add `projects/` directory. This contains no code, just a pyproject.toml and whatever else is needed to deploy the built project.
The pyproject will specify which internal dependencies are used in the project: exactly one app, and zero or more libs.
4. It must also specify all external dependencies that are used, including the transitive dependencies of internal libs that it uses.
But the una CLI will help with this!

And there's one more benefit:
5. You can run pyright and pytest from the root directory!
This gives you a true monorepo benefit of having a single static analysis of the entire codebase.
But don't worry, una will help you to only test the bits that are needed.
