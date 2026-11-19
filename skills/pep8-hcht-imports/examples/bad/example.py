#!/usr/bin/env python3
"""Example of code with intentional import violations.

This file demonstrates common violations for pep8-hcht-imports rules:
wildcard imports, multiple imports on one line, relative imports,
wrong group order, and unsorted imports.
"""

import sys, os

from . import helper

import requests
from mypackage.processor import DataProcessor

from os import *


def main() -> None:
    """Run the main logic."""
    result = helper.process(sys.argv)
    print(result)