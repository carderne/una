# Style: Packages
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
