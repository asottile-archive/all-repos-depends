[![Build Status](https://dev.azure.com/asottile/asottile/_apis/build/status/asottile.all-repos-depends?branchName=master)](https://dev.azure.com/asottile/asottile/_build/latest?definitionId=34&branchName=master)
[![Azure DevOps coverage](https://img.shields.io/azure-devops/coverage/asottile/asottile/34/master.svg)](https://dev.azure.com/asottile/asottile/_build/latest?definitionId=34&branchName=master)

all-repos-depends
=================

View the dependencies of your repositories.

`all-repos-depends` is an add-on project to
[all-repos](https://github.com/asottile/all-repos).

## Installation

`pip install all-repos-depends`


## CLI

To generate the database, run `all-repos-depends-generate`.

To run the webapp, run `all-repos-depends-server`.  The server runs on a
configurable `--port`.


## configuration

```json
{
    "all_repos_config": "../all-repos/all-repos.json",
    "get_packages": [
        "all_repos_depends.packages.setup_py",
        "all_repos_depends.packages.package_json"
    ],
    "get_depends": [
        "all_repos_depends.depends.setup_py",
        "all_repos_depends.depends.requirements_tools"
    ]
}
```

## providers

Providers are the pluggable bits of `all-repos-depends`.  A few providers are
given for free.

The types that the providers will produce are in `all_repos_depends.types`:

```python
Package = collections.namedtuple('Package', ('type', 'key', 'name'))
Depends = collections.namedtuple(
    'Depends', ('relationship', 'package_type', 'package_key', 'spec'),
)
```

If a provider encounters a detectable error state, it should raise an
exception of the type `all_repos_depends.errors.DependsError`.

### `package` providers

A `package` provider will be called while the `cwd` is at the root of the
repository.  It must return a `all_repos_depends.types.Package` that the
repository provides (or `None` if it is not applicable).

A few are provided out of the box (PRs welcome for more!)

#### `all_repos_depends.packages.setup_py`

This `package` provider reads the ast of `setup.py` and searches for the
`name` keyword argument.  For now this means it will only be able to read
`setup.py` files which have python3-compatible syntax and set their name
literally.

#### `all_repos_depends.packages.package_json`

Reads the `name` field out of an npm `package.json` file.

### `depends` providers

A `depends` provider will be called while the `cwd` is at the root of the
repository.  It must return a sequence or `all_repos_depends.types.Depends`
that the repository provides (or an empty sequence if it is not applicable).

#### `all_repos_depends.depends.setup_py`

This `depends` provider reads the ast of `setup.py` and searches for the
`install_requires` keyword argument.

#### `all_repos_depends.depends.requirements_tools`

This `depends` provider reads the following requirements files according to
the conventions for
[requirements-tools](https://github.com/Yelp/requirements-tools):

- `requirements-minimal.txt` (`DEPENDS`)
- `requirements.txt` (`REQUIRES`)
- `requirements-dev-minimal.txt` (`DEPENDS_DEV`)
- `requirements-dev.txt` (`REQUIRES_DEV` if `-minimal` is present otherwise
  `DEPENDS_DEV`)
