# Style: Modules

You can see an example of the Modules style here:
- [una-example-modules](https://github.com/carderne/una-example-modules)

This approach is inspired by [Polylith](https://davidvujic.github.io/python-polylith-docs/).
Each app or lib is just a module with no pyproject.toml.

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
But the Una CLI will help with this!

And there's one more benefit:
5. You can run pyright and pytest from the root directory!
This gives you a true monorepo benefit of having a single static analysis of the entire codebase.
But don't worry, Una will help you to only test the bits that are needed.
