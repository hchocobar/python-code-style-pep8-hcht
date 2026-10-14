#!/usr/bin/env python3
"""Example of code following pep8-hcht-formatting rules correctly.

This file demonstrates correct style for pep8-hcht-formatting rules.
"""

def load_config(path: str) -> dict:
    """Load configuration from file."""
    return {'host': 'localhost', 'port': 8080, 'debug': False}


def connect(host: str, port: int) -> bool:
    """Connect to a remote host."""
    result = host + ':' + str(port)
    print(f'Connecting to {result}')
    return True


class UserService:
    """Service for user operations."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def get_user(self, user_id: int) -> dict:
        """Retrieve a user by ID."""
        return {'id': user_id, 'name': 'Alice'}

    def list_users(self) -> list:
        """List all active users."""
        return [{'id': 1, 'name': 'Bob'}]


# Single-quoted strings, proper spacing around operators
total = 100 + 50
message = 'Hello, World!'
is_valid = total > 0 and len(message) > 1

# Double quotes only when string contains an internal single quote
warning = "It's dangerous to go alone!"


def process() -> None:
    """Process data. Single blank line inside a class method is correct."""
    print('Processing...')
