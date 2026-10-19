#!/usr/bin/env python3
"""Tests for pep8-hcht-naming style rules."""

from pathlib import Path
import sys

import pytest

# Add scripts directory to path for imports
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from check_naming import check_naming, _is_snake_case, _is_upper_snake_case
from check_naming import _is_pascal_case, _is_descriptive

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"


@pytest.fixture
def good_example() -> Path:
    return EXAMPLES_DIR / "good" / "example.py"


@pytest.fixture
def bad_example() -> Path:
    return EXAMPLES_DIR / "bad" / "example.py"


# ---------------------------------------------------------------------------
# Utility tests
# ---------------------------------------------------------------------------

class TestSnakeCase:
    """Tests for _is_snake_case utility."""

    def test_valid_snake_case(self) -> None:
        assert _is_snake_case("my_variable")
        assert _is_snake_case("process_data")
        assert _is_snake_case("get_user_by_id")
        assert _is_snake_case("a")
        assert _is_snake_case("_private")
        assert _is_snake_case("__dunder__")

    def test_invalid_snake_case(self) -> None:
        assert not _is_snake_case("myVariable")
        assert not _is_snake_case("MyVariable")
        assert not _is_snake_case("MY_CONSTANT")
        assert not _is_snake_case("ProcessData")


class TestUpperSnakeCase:
    """Tests for _is_upper_snake_case utility."""

    def test_valid_upper_snake_case(self) -> None:
        assert _is_upper_snake_case("MAX_RETRIES")
        assert _is_upper_snake_case("DEFAULT_TIMEOUT")
        assert _is_upper_snake_case("API_BASE_URL")
        assert _is_upper_snake_case("A")
        assert _is_upper_snake_case("_PRIVATE_CONST")

    def test_invalid_upper_snake_case(self) -> None:
        assert not _is_upper_snake_case("MaxRetries")
        assert not _is_upper_snake_case("DEFAULT_Timeout")
        assert not _is_upper_snake_case("default_timeout")
        assert not _is_upper_snake_case("Default")


class TestPascalCase:
    """Tests for _is_pascal_case utility."""

    def test_valid_pascal_case(self) -> None:
        assert _is_pascal_case("DataProcessor")
        assert _is_pascal_case("HTMLParser")
        assert _is_pascal_case("HTTPConnection")
        assert _is_pascal_case("UserProfile")
        assert _is_pascal_case("A")

    def test_invalid_pascal_case(self) -> None:
        assert not _is_pascal_case("dataProcessor")
        assert not _is_pascal_case("data_processor")
        assert not _is_pascal_case("myClass")
        assert not _is_pascal_case("MY_CONSTANT")


class TestDescriptive:
    """Tests for _is_descriptive utility."""

    def test_descriptive_names(self) -> None:
        assert _is_descriptive("element")
        assert _is_descriptive("response")
        assert _is_descriptive("result")
        assert _is_descriptive("processor")
        assert _is_descriptive("connection")
        assert _is_descriptive("user_id")
        assert _is_descriptive("calculate_average")
        assert _is_descriptive("DataProcessor")
        assert _is_descriptive("MAX_RETRIES")

    def test_allowed_short_names(self) -> None:
        assert _is_descriptive("i")
        assert _is_descriptive("j")
        assert _is_descriptive("k")
        assert _is_descriptive("e")
        assert _is_descriptive("T")
        assert _is_descriptive("df")
        assert _is_descriptive("fn")
        assert _is_descriptive("_")

    def test_non_descriptive_abbreviations(self) -> None:
        assert not _is_descriptive("elem")
        assert not _is_descriptive("resp")
        assert not _is_descriptive("tmp")
        assert not _is_descriptive("cfg")
        assert not _is_descriptive("val")
        assert not _is_descriptive("arr")
        assert not _is_descriptive("obj")
        assert not _is_descriptive("ret")
        assert not _is_descriptive("msg")
        assert not _is_descriptive("ctx")
        assert not _is_descriptive("db")
        assert not _is_descriptive("cli")

    def test_single_letter_non_allowed(self) -> None:
        assert not _is_descriptive("a")
        assert not _is_descriptive("q")
        assert not _is_descriptive("p")
        assert not _is_descriptive("c")
        assert not _is_descriptive("m")


# ---------------------------------------------------------------------------
# Checker integration tests
# ---------------------------------------------------------------------------

class TestCheckNaming:
    """Tests for the check_naming function."""

    def test_good_example_no_violations(self, good_example: Path) -> None:
        """Verify the good example has zero violations."""
        source = good_example.read_text(encoding="utf-8")
        violations = check_naming(source, good_example)
        assert violations == [], (
            f"Expected no violations, got {len(violations)}:\n"
            + "\n".join(f"  - {v}" for v in violations)
        )

    def test_bad_example_has_violations(self, bad_example: Path) -> None:
        """Verify the bad example has violations."""
        source = bad_example.read_text(encoding="utf-8")
        violations = check_naming(source, bad_example)
        assert len(violations) > 0, (
            "Expected violations in bad example, got none"
        )

    def test_bad_example_class_violations(self, bad_example: Path) -> None:
        """Verify class naming violations are detected."""
        source = bad_example.read_text(encoding="utf-8")
        violations = check_naming(source, bad_example)
        class_msgs = [v for v in violations if "Class" in v]
        assert any("data_processor" in v for v in class_msgs), (
            "Should detect data_processor as wrong case"
        )
        assert any("htmlParser" in v for v in class_msgs), (
            "Should detect htmlParser as wrong case"
        )

    def test_bad_example_function_violations(self, bad_example: Path) -> None:
        """Verify function naming violations are detected."""
        source = bad_example.read_text(encoding="utf-8")
        violations = check_naming(source, bad_example)
        func_msgs = [v for v in violations if "Function" in v]
        assert any("ProcessRequest" in v for v in func_msgs), (
            "Should detect ProcessRequest as wrong case"
        )
        assert any("getData" in v for v in func_msgs), (
            "Should detect getData as wrong case"
        )

    def test_bad_example_abbreviation_violations(self,
                                                  bad_example: Path) -> None:
        """Verify abbreviated names are detected."""
        source = bad_example.read_text(encoding="utf-8")
        violations = check_naming(source, bad_example)
        abbr_msgs = " ".join(violations).lower()
        assert "elem" in abbr_msgs, "Should detect 'elem' as abbreviated"
        assert "resp" in abbr_msgs, "Should detect 'resp' as abbreviated"
        assert "tmp" in abbr_msgs, "Should detect 'tmp' as abbreviated"

    def test_method_case_violations(self, bad_example: Path) -> None:
        """Verify method naming violations are detected."""
        source = bad_example.read_text(encoding="utf-8")
        violations = check_naming(source, bad_example)
        method_msgs = [v for v in violations if "Function" in v]
        assert any("FetchData" in v for v in method_msgs), (
            "Should detect FetchData method as wrong case"
        )
        assert any("_Parse_Response" in v for v in method_msgs), (
            "Should detect _Parse_Response method as wrong case"
        )

    def test_constant_case_violations(self, bad_example: Path) -> None:
        """Verify constant naming violations are detected."""
        source = bad_example.read_text(encoding="utf-8")
        violations = check_naming(source, bad_example)
        const_msgs = " ".join(violations)
        # max_retries (lowercase, module-level) - this might be flagged as
        # wrong case for a constant
        assert "max_retries" in const_msgs or "DEFAULT_Timeout" in const_msgs, (
            "Should detect constant case violations"
        )


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestCheckNamingEdgeCases:
    """Tests for edge cases in naming checks."""

    def test_empty_file(self) -> None:
        """Verify empty file has no violations."""
        violations = check_naming("", Path("/tmp/empty.py"))
        assert violations == []

    def test_syntax_error(self) -> None:
        """Verify syntax error returns a violation."""
        violations = check_naming(
            "def broken(", Path("/tmp/broken.py")
        )
        assert len(violations) == 1
        assert "Syntax error" in violations[0]

    def test_dunder_methods_allowed(self) -> None:
        """Verify dunder methods are not flagged."""
        source = """
class MyClass:
    def __init__(self):
        pass
    def __str__(self):
        return "MyClass"
"""
        violations = check_naming(source, Path("/tmp/test.py"))
        dunder_violations = [
            v for v in violations if "__init__" in v or "__str__" in v
        ]
        assert len(dunder_violations) == 0, (
            f"Dunder methods should not be flagged: {dunder_violations}"
        )

    def test_self_and_cls_allowed(self) -> None:
        """Verify 'self' and 'cls' parameters are not flagged."""
        source = """
class MyClass:
    def method(self, param_one: int) -> None:
        pass

    @classmethod
    def create(cls, param_two: str) -> "MyClass":
        return MyClass()
"""
        violations = check_naming(source, Path("/tmp/test.py"))
        param_violations = [
            v for v in violations if "'self'" in v or "'cls'" in v
        ]
        assert len(param_violations) == 0, (
            f"'self' and 'cls' should not be flagged: {param_violations}"
        )

    def test_loop_variable_allowed_short(self) -> None:
        """Verify standard loop variables (i, j, k) are allowed."""
        source = """
def example():
    for i in range(10):
        print(i)
    for j, k in zip(range(5), range(5)):
        print(j, k)
"""
        violations = check_naming(source, Path("/tmp/test.py"))
        loop_violations = [
            v for v in violations
            if "'i'" in v or "'j'" in v or "'k'" in v
        ]
        # Only flag if they appear as non-descriptive
        nondesc = [v for v in loop_violations if "descriptive" in v.lower()]
        assert len(nondesc) == 0, (
            f"Standard loop vars should not be flagged: {nondesc}"
        )

    def test_underscore_throwaway_allowed(self) -> None:
        """Verify underscore throwaway variable is allowed."""
        source = """
def example():
    for _ in range(10):
        pass
    _, second = (1, 2)
    print(second)
"""
        violations = check_naming(source, Path("/tmp/test.py"))
        under_violations = [
            v for v in violations if "'_'" in v
        ]
        assert len(under_violations) == 0, (
            f"Underscore should not be flagged: {under_violations}"
        )

    def test_exception_variable_allowed(self) -> None:
        """Verify 'e' as exception variable is allowed."""
        source = """
def example():
    try:
        risky_operation()
    except ValueError as e:
        print(e)
"""
        violations = check_naming(source, Path("/tmp/test.py"))
        exc_violations = [
            v for v in violations if "Exception variable" in v
        ]
        assert len(exc_violations) == 0, (
            f"Exception var 'e' should not be flagged: {exc_violations}"
        )

    def test_module_level_constants_upper(self) -> None:
        """Verify UPPER_SNAKE_CASE constants are not flagged."""
        source = """
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
API_BASE_URL = "https://example.com"
"""
        violations = check_naming(source, Path("/tmp/test.py"))
        # These should not be violations
        const_violations = [
            v for v in violations
            if any(name in v for name in
                   ["MAX_RETRIES", "DEFAULT_TIMEOUT", "API_BASE_URL"])
        ]
        assert len(const_violations) == 0, (
            f"Valid constants should not be flagged: {const_violations}"
        )


# ---------------------------------------------------------------------------
# Example files existence
# ---------------------------------------------------------------------------

class TestExampleFiles:
    """Verify example files are present."""

    def test_good_example_exists(self, good_example: Path) -> None:
        assert good_example.exists(), f"Missing: {good_example}"

    def test_bad_example_exists(self, bad_example: Path) -> None:
        assert bad_example.exists(), f"Missing: {bad_example}"