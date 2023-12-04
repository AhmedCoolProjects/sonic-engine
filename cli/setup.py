#!/usr/bin/env python

VERSION = "1.4.3"

__authors__ = ["Soufiane Oualil", "Ahmed Bargady"]
__contact__ = "www.google.com"
__copyright__ = "Copyright 2022, AtlasSonic"
__credits__ = ["Soufinae Oualil"]
__date__ = "2023/07/17"
__deprecated__ = False
__email__ = "someone@um6p.ma"
__license__ = "MIT"
__maintainer__ = "developer"
__status__ = "Development"
__version__ = VERSION

from setuptools import setup, find_packages

setup(
    name="sonic-engine-cli",
    version=VERSION,
    packages=find_packages(),
    author="Soufiane Oualil, Ahmed Bargady",
    description="Sonic Engine is a python package for the AtlasSonic project",
    entry_points={
        "console_scripts": [
            "sengine-cli = sengine_cli.__main__:main"
        ]
    },
    install_requires=["pyaml", "redis == 4.2.2",
                      "numpy", "pytest", "yapsy", "flask"]
)
