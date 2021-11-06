# Data Mining (ID2222)

## Package manager

Uses `poetry` as package manager.

**NOTE** although there's no need at this point, the only packages added for homework 1 is for easier debugging with `ipdb` and `ipython`, as well as auto-formatting with `black`.

### Install poetry

```sh
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

### Use poetry

```sh
# Install packages
poetry install

# Enter shell like in virtualenv
poetry shell

# OR prepend each command with
poetry run
```
