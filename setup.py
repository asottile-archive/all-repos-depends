from setuptools import find_packages
from setuptools import setup

setup(
    name='all_repos_depends',
    description='View the dependencies of your repositories.',
    url='https://github.com/asottile/all-repos-depends',
    version='0.0.0',
    author='Anthony Sottile',
    author_email='asottile@umich.edu',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=['all-repos>=1.3.0', 'flask', 'mako', 'packaging'],
    packages=find_packages(exclude=('tests*', 'testing*')),
    package_data={'all_repos_depends': ['templates/*.mako']},
    entry_points={
        'console_scripts': [
            'all-repos-depends-generate=all_repos_depends.generate:main',
            'all-repos-depends-server=all_repos_depends.server:main',
        ],
    },
)
