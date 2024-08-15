# Type-checking, testing, editors
## Pyright
With the `packages` style (the default), you'll need do Pyright type-checking on a per-package basis.

That is, you should add something like the config below to each `apps/*/pyproject.toml` and `libs/*/pyproject.toml`.

With the `modules` style this is not necessary, and you can just have one root Pyright (and Pytest!).

```toml
[tool.pyright]
venvPath = "../.."
venv = ".venv"
pythonVersion = "3.11"
strict = ["**/*.py"]
```
