#!/usr/bin/env python3
"""Example of code with intentional vertical alignment violations."""


# Rule 2: Hanging indent in function definition
# Continuation uses fixed 4-space indent instead of aligning with first param
def some_function(param_one,
    param_two,
    param_three):
    return param_one + param_two + param_three


# Rule 2: Hanging indent in function call + Rule 5: bracket on own line
result = some_function(100,
    200,
    300
    )


# Rule 2: Hanging indent in chained call (not aligned with first arg)
result = (df.filter(
        condition)
           .groupby(col))


# Rule 2: Hanging indent in dict items (continuation at 4 spaces)
config = {
    'host': 'localhost',
    'port': 8080,
    'debug': False,
}


# Rule 2: Hanging indent in list items
items = [
    'alpha',
    'beta',
    'gamma',
]


# Rule 2: Hanging indent in tuple items
values = (
    1,
    2,
    3,
)


# Rule 4: Binary operator at end of line (should be at start)
formula = (condition_one and
           condition_two or
           condition_three)


# Rule 5: Closing bracket on its own line
config2 = {host: 'localhost',
           port: 8080,
           debug: False,
           }


# Rule 6: Split string (implicit concatenation across lines)
message = ('Lorem ipsum dolor sit amet '
           'consectetur adipiscing elit')


# Rule 6: Split string in function call
violations.append(
    f'Expected 0 violations, got '
    f'{len(violations)}')


# Rule 7: Operator at end of line in if (should be at start)
if (condition_one and
    condition_two or
    condition_three):
    pass


# Rule 2: Hanging indent in comprehension
active_users = [
    user
    for user in users
    if user.is_active
]


# Rule 4: Backslash line continuation (prohibited)
value = condition_one \
        and condition_two

