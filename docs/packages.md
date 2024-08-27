# Packages

You can see an example of this here:

- [una-example](https://github.com/carderne/una-example)

The structure will look something like the below. This is completely up to you though! Whatever glob patterns you specify in uv's [Workspace](https://docs.astral.sh/uv/concepts/workspaces/) `members` table will be supported.
```bash
.
├── pyproject.toml
├── uv.lock
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

At build-time, Una will do the following:

1. Read the list of internal dependencies (more on this shortly) and inject them into the build.
2. Read all external requirements of those dependencies, and add them to the dependency table.

You can use the Una CLI tool to ensure that all internal dependencies are kept in sync.

1. Use a uv workspace:
```toml
# /pyproject.toml
[tool.uv]
dev-dependencies = []

[tool.uv.workspace]
members = ["apps/*", "libs/*"]
# this could also be something like below
# if you don't want to separate apps and libs
# members = ["packages/*"]
```

2. Create your packages as you like.
3. Add external dependencies to your packages as normal.
Then, to add an internal dependency to an app, we do the following in its pyproject.toml. This tells uv (and Una!) to find the `greeter` package locally in the workspace.

```toml
# /apps/server/pyproject.toml
[project]
dependencies = ["greeter"]

[tool.uv.sources]
greeter = { workspace = true }

[build-system]
requires = ["hatchling", "hatch-una"]
build-backend = "hatchling.build"

[tool.hatch.build.hooks.una-build]
[tool.hatch.build.hooks.una-meta]
```

4. Then you can build from that package directory and Una will inject everything that is needed:
```bash
uvx --from build pyproject-build --installer uv
```

5. Once you have your built `.whl` file, all you need in your Dockerfile is:
```Dockerfile
FROM python
COPY dist dist
RUN pip install dist/*.whl
```
