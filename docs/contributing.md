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

## Setup Rye
Install it if needed (full instructions [here](https://rye.astral.sh/)):
```bash
curl -sSf https://rye.astral.sh/get | bash
```

Then sync your local environment:
```bash
rye sync
```

## Run all code quality checks
```bash
rye run fmt
rye run lint
rye run check
rye run test

# or
rye run all
```

## Open a PR
Push your changes to your branch on your fork, then open a PR against the main repository.
