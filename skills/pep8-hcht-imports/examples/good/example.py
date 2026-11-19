#!/usr/bin/env python3
"""Example of code following pep8-hcht-imports rules correctly.

This file demonstrates correct import style: one import per line,
grouped in the correct order (stdlib, third_party, local) with
blank lines between groups, alphabetically sorted within groups,
and no wildcard or relative imports.
"""

import os
import sys

import requests

from mypackage import helper
from mypackage.processor import DataProcessor


def main() -> None:
    """Run the main logic."""
    result = helper.process(sys.argv)
    print(result)