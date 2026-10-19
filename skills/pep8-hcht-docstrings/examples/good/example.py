"""Example module with correct NumPy-style docstrings for all functions."""

def add(first: int, second: int) -> int:
    """Add two integers and return the result.

    Parameters
    ----------
    first : int
        The first addend.
    second : int
        The second addend.

    Returns
    -------
    int
        The sum of first and second.
    """
    return first + second


def greet(name: str) -> str:
    """Generate a greeting message for the given name.

    Parameters
    ----------
    name : str
        The person's name.

    Returns
    -------
    str
        A greeting string.
    """
    return 'Hello, ' + name + '!'


class Calculator:
    """A simple calculator class."""

    def __init__(self, factor: float = 1.0) -> None:
        """Initialize the calculator with a multiplier factor.

        Parameters
        ----------
        factor : float, optional
            The multiplier factor (default is 1.0).
        """
        self.factor = factor

    def multiply(self, value: float) -> float:
        """Multiply a value by the internal factor.

        Parameters
        ----------
        value : float
            The value to multiply.

        Returns
        -------
        float
            The multiplied result.
        """
        return value * self.factor

