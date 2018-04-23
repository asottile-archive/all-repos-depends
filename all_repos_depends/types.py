import collections

Repo = collections.namedtuple(
    'Repo', ('name', 'packages', 'depends', 'errors'),
)
Package = collections.namedtuple('Package', ('type', 'key', 'name'))
Depends = collections.namedtuple(
    'Depends', ('relationship', 'package_type', 'package_key', 'spec'),
)
