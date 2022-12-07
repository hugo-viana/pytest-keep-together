# pytest-keep-together
Pytest plugin to customize test ordering by running all "related" tests together.

# Usage

TBD

# Installation

Create a new virtual environment, activate it and install development requirements:

```
pip install requirements_dev.txt
```

# Development best-practices

Every commit must be checked with flake8 and mypy:

```
flake8
```

```
mypy .
```

# Build and distribute a new version

## Build package

```
py -m build
```

## Publish new version to test PyPi

```
py -m twine upload --repository testpypi dist/*
```

## Publish new version to PyPi (production)

```
py -m twine upload dist/*
```
