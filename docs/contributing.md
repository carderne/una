# Contributing

The usual process to make a contribution is to:

1. Check for existing related issues
2. Fork the repository and create a new branch
3. Make your changes
4. Make sure formatting, linting and tests passes.
5. Add tests if possible to cover the lines you added.
6. Commit, and send a Pull Request.

## Fork the repository
So that you have your own copy.

## Clone the repository

```bash
git clone git@github.com:your-username/una.git
cd una
git checkout -b add-my-contribution
```

## Setup uv
Install it if needed (full instructions [here](https://docs.astral.sh/uv/getting-started/installation/)):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then sync your local environment:
```bash
uv sync
```

## Run all code quality checks
```bash
make fmt
make lint
make check
make test

# or
make all
```

## Open a PR
Push your changes to your branch on your fork, then open a PR against the main repository.
