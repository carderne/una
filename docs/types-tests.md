# Types and tests
## Pyright
You'll need to configure pyright for each package.

That is, you should add something like the config below to each `apps/*/pyproject.toml` and `libs/*/pyproject.toml`.

```toml
[tool.pyright]
venvPath = "../.."
venv = ".venv"
pythonVersion = "3.11"
strict = ["**/*.py"]
```

Once that is added, you can run `rye run pyright` in the root and it should work correctly.

## Pytest
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
