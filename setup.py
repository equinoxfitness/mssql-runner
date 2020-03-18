import os
import re
from setuptools import setup, find_packages

requires = [
    'datacoco-core==0.1.1',
    'datacoco-cloud==0.1.9',
    'datacoco-db==0.1.6',
    'datacoco-batch==0.1.1',
    'datacoco-secretsmanager==0.1.4'
]


def get_version():
    version_file = open(os.path.join("mssql_runner", "__version__.py"))
    version_contents = version_file.read()
    return re.search('__version__ = "(.*?)"', version_contents).group(1)


setup(
    name="mssql_runner",
    packages=find_packages(exclude=["tests*"]),
    version=get_version(),
    license="MIT",
    description="MSSQL runner by Equinox",
    long_description=open("README.rst").read(),
    author="Equinox Fitness",
    install_requires=requires,
    scripts=['bin/mssql-runner'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
    ],
)
