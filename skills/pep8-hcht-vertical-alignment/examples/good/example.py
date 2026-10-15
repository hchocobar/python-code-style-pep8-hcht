#!/usr/bin/env python3
"""Example of code following vertical alignment rules correctly."""
import pandas as pd

# Rule 2: Vertical alignment in function definitions
def calculate_total(price: float,
                    quantity: int,
                    tax: float) -> float:
    """Calculate total price with tax."""
    return price * quantity * (1 + tax)


def load_data(filepath: str,
              sep: str = ',',
              encoding: str = 'utf-8') -> pd.DataFrame:
    """Load data from file."""
    return pd.read_csv(filepath, sep = sep, encoding = encoding)


# Rule 2: Vertical alignment in function calls
result = calculate_total(29.99,
                         3,
                         0.21)


# Rule 2: Vertical alignment in list items
items = ['alpha', 'beta', 'gamma', 'delta',
         'epsilon', 'zeta', 'eta', 'theta']


# Rule 2: Vertical alignment in dict items
config = {host: 'localhost',
          port: 8080,
          debug: False}


# Rule 2: Vertical alignment in comprehension
active_users = [user
                for user in users
                if user.is_active
                and user.email is not None]


# Rule 2: Vertical alignment in keyword args
book = Book(title = 'Clean Code',
            author = 'Robert C. Martin',
            year = 2008,
            publisher = 'Prentice Hall',
            isbn = '978-0132350884',
            pages = 464)


# Rule 2: Vertical alignment in nested call
df = pd.DataFrame({'name': ['Alice', 'Bob'],
                   'age': [30, 25],
                   'city': ['New York', 'London']})


# Rule 3: Chained method calls (parentheses required for multi-line)
result = (df.filter(condition)
           .groupby(col)
           .head(10))


# Rule 4: Binary operators at start of line inside parentheses
result = (condition_one
          and condition_two
          or condition_three)


# Rule 5: Closing bracket at end of last item (no trailing comma)
result = (condition_one
          and condition_two
          or condition_three)


# Rule 6: Strings on a single line (not split)
violations.append('Expected 0 violations, got 2: line 42, line 57')


# Rule 7: If with vertical alignment (operators at start)
if (user.is_active
    and not user.is_banned
    and user.role == 'admin'):
    grant_access()


# Rule 7: While with vertical alignment
while (count < max_retries
       and not result.is_ready):
    count += 1
    sleep(delay)

