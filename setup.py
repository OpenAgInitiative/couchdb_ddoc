from setuptools import setup, find_packages
from os import path

readme_path = path.join(path.dirname(__file__), "README.md")
with open(readme_path) as f:
    readme = f.read()

setup(
    name='couchdb_ddoc',
    version='0.0.1',
    author='OpenAgricultureInitiative',
    description='Command line utility for working with CouchDB design documents',
    long_description=readme,
    license="GPL-3.0",
    url="https://github.com/OpenAgInitiative/couchdb_ddoc",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2.7",
    ],
    packages=find_packages(exclude=("tests", "tests.*")),
    install_requires=[
        "CouchDB>=1.0"
    ],
    extras_require={},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'ddoc_load_fixture=ddoc:cli_load_fixture'
        ]
    }
)
