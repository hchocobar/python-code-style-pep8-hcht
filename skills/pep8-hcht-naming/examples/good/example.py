#!/usr/bin/env python3
"""Example of code following pep8-hcht-naming rules correctly.

This file demonstrates correct naming conventions.
"""

from typing import TypeVar

# --- Constants (UPPER_SNAKE_CASE) ---
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
API_BASE_URL = "https://api.example.com"


# --- Classes (PascalCase) ---
class DataProcessor:
    """Processes data from external sources."""

    def __init__(self, endpoint_url: str, timeout: int = DEFAULT_TIMEOUT) -> None:
        self.endpoint_url = endpoint_url
        self.timeout = timeout
        self._results: list[dict] = []

    def fetch_data(self) -> list[dict]:
        """Retrieves data from the configured endpoint."""
        response = self._make_request()
        records = self._parse_response(response)
        return records

    def _make_request(self) -> str:
        """Simulates an HTTP request (for illustration)."""
        return '{"items": []}'

    def _parse_response(self, raw_response: str) -> list[dict]:
        """Parses JSON response into a list of dictionaries."""
        import json
        data = json.loads(raw_response)
        return data.get("items", [])


class HTMLParser:
    """Parses HTML content into structured data."""

    def parse(self, html_content: str) -> str:
        """Extracts text content from HTML."""
        element = "<tag></tag>"
        return element


class HTTPConnection:
    """Manages HTTP connection lifecycle."""

    def connect(self, host: str, port: int = 443) -> bool:
        """Establishes a connection to the given host."""
        return True


# --- Functions (snake_case) ---
def calculate_average(numbers: list[float]) -> float:
    """Computes the mean of a list of numbers."""
    if not numbers:
        return 0.0
    total = sum(numbers)
    count = len(numbers)
    return total / count


def process_user_request(request_data: dict) -> dict:
    """Processes an incoming user request and returns a response."""
    user_id = request_data.get("user_id")
    action = request_data.get("action", "view")
    return {"user_id": user_id, "action": action, "status": "ok"}


def main() -> None:
    """Entry point demonstrating correct naming."""
    processor = DataProcessor(API_BASE_URL)
    results = processor.fetch_data()
    average = calculate_average([1.0, 2.0, 3.0])
    print(f"Results: {len(results)}, Average: {average}")


# --- Allowed short names ---
def sum_values(values: list[int]) -> int:
    """Uses 'i' as loop index (allowed exception)."""
    total = 0
    for i in values:
        total += i
    return total


if __name__ == "__main__":
    main()