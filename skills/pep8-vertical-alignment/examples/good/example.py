#!/usr/bin/env python3
"""Example of code following vertical alignment rules correctly."""
import pandas as pd


def calculate_total(price: float,
                    quantity: int,
                    tax: float) -> float:
    """Calculate total price with tax.

    Parameters
    ----------
    price : float
        Unit price.
    quantity : int
        Number of items.
    tax : float
        Tax rate.

    Returns
    -------
    float
        Total price.
    """
    return price * quantity * (1 + tax)


def load_data(filepath: str,
              sep: str = ",",
              encoding: str = "utf-8") -> pd.DataFrame:
    """Load data from file.

    Parameters
    ----------
    filepath : str
        Path to data file.
    sep : str
        Column separator.
    encoding : str
        File encoding.

    Returns
    -------
    pd.DataFrame
        Loaded data.
    """
    return pd.read_csv(filepath, sep=sep, encoding=encoding)


result = calculate_total(29.99,
                         3,
                         0.21)


items = ["alpha", "beta", "gamma", "delta",
         "epsilon", "zeta", "eta", "theta"]


config = {host: "localhost",
          port: 8080,
          debug: False}


active_users = [user
                for user in users
                if user.is_active
                and user.email is not None]


book = Book(title="Clean Code",
            author="Robert C. Martin",
            year=2008,
            publisher="Prentice Hall",
            isbn="978-0132350884",
            pages=464)


df = pd.DataFrame({"name": ["Alice", "Bob"],
                   "age": [30, 25],
                   "city": ["New York", "London"]})
result = (df.filter(condition)
          .groupby(col)
          .head(10))


if (user.is_active
    and not user.is_banned
    and user.role == "admin"):
    grant_access()


result = (condition_one
          and condition_two
          or condition_three)