"""Example module with docstring violations."""

def missing_docstring(first: int, second: int) -> int:
    """This function uses Google style instead of NumPy.

    Args:
        first (int): First number.
        second (int): Second number.

    Returns:
        int: The sum.
    """
    return first + second


def no_docstring_at_all(value: float) -> float:
    return value * 2


def blank_line_after_docstring() -> None:
    """This docstring has a blank line after the closing triple quote."""

    print('Line follows docstring directly')


def rest_style(param_one: str) -> str:
    """Docstring with reST-style directives.

    :param param_one: A parameter documented in reST style.
    :type param_one: str
    :return: The processed string.
    :rtype: str
    """
    return param_one.upper()


class DataProcessor:
    """A class that processes data."""

    def run(self, data: list[float]) -> list[float]:
        """Filter and process data using the threshold.

        Returns
        -------
        list[float]
            The filtered values.
        """
        return [x for x in data if x > 0.5]

    def transform(self, values: list[float]) -> list[float]:
        return [element * 2 for element in values]

