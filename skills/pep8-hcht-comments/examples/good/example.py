#!/usr/bin/env python3
"""
Example of code following pep8-hcht-comments rules correctly.

This file demonstrates the correct comment style: one space after the
hash, a capital letter at the start, two spaces before inline comments
and no decorative comment blocks.
"""


def calculate_total(price: float, tax: float) -> float:
    """Calculate the total amount with tax."""
    return price + tax


# Configuration values are documented here
config = {'host': 'localhost',
          'port': 8080,
          'debug': False}

# URL fragments are part of the string, not comments
url = 'http://example.com/page#section'

total = calculate_total(19.99, 2.50)  # Total amount