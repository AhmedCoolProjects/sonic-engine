#!/usr/bin/env python
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
__version__ = "2.1.10"

import sys
import setuptools

if not sys.version_info >= (3, 7):
    sys.exit("Sorry, python3.7+ is required for this package")

setuptools.setup(
    name="sonic_engine",
    version="2.1.10",
    url="https://github.com/AhmedCoolProjects/sonic-engine",
    author_email="ahmed.baragdy@outlook.com",
    author="Soufiane Oualil, Ahmed Bargady",
    description="Sonic Engine is a python package for the AtlasSonic project",
    packages=setuptools.find_packages(),
    install_requires=["pyaml", "redis == 4.2.2", "numpy", "pytest", "yapsy", "flask"],
)
