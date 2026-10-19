#!/usr/bin/env python3
"""Example of code with intentional naming violations.

This file demonstrates common naming violations for pep8-hcht-naming rules.
"""

# --- Constants using wrong case ---
max_retries = 3              # Violation: should be UPPER_SNAKE_CASE
DEFAULT_Timeout = 30         # Violation: mixed case in constant


# --- Class naming violations ---
class data_processor:         # Violation: should be PascalCase
    """Processes data."""

    def FetchData(self):      # Violation: method should be snake_case
        """Retrieves data."""
        return []

    def _Parse_Response(self, raw):  # Violation: method should be snake_case
        """Parses response."""
        return raw


class htmlParser:              # Violation: should be PascalCase (capital H)
    """Parses HTML."""

    def parseHTML(self, content):  # Violation: method should be snake_case
        """Extracts HTML content."""
        return content


# --- Function naming violations ---
def ProcessRequest(req_data):  # Violation: should be snake_case
    """Processes a request."""
    return req_data


def getData():                 # Violation: should be snake_case
    """Gets data."""
    return []


def calc_avg(nums):            # Violation: 'nums' is abbreviated
    """Calculates average."""
    if not nums:
        return 0.0
    total = sum(nums)
    return total / len(nums)


# --- Variable naming violations ---
def example_functions() -> None:
    """Demonstrates variable naming violations."""
    elem = "<tag></tag>"       # Violation: abbreviated name
    resp = "ok"                # Violation: abbreviated name
    tmp = 42                   # Violation: abbreviated name
    cfg = {"key": "value"}     # Violation: abbreviated name
    n = 10                     # Violation: 'n' allowed only as loop counter
    val = 100                  # Violation: abbreviated name
    arr = [1, 2, 3]            # Violation: abbreviated name
    obj = {}                   # Violation: abbreviated name
    ret = True                 # Violation: abbreviated name
    msg = "hello"              # Violation: abbreviated name


# --- Single-letter variables (non-standard) ---
def bad_loop() -> None:
    """Demonstrates non-standard single-letter names."""
    a = [1, 2, 3]              # Violation: non-descriptive single letter
    for q in a:                # Violation: 'q' not in allowed short names
        print(q)


# --- Mixed naming in the same context ---
def main() -> None:
    """Entry point."""
    maxCount = 100             # Violation: should be snake_case
    DB_CONN = "sqlite://"      # Violation: local variable, not constant
    DB_Url = "localhost"       # Violation: mixed case
    p = "test"                 # Violation: non-descriptive single letter
    print(maxCount)


if __name__ == "__main__":
    main()