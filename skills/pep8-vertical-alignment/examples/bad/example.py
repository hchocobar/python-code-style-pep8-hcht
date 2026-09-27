#!/usr/bin/env python3
"""Example of code with intentional vertical alignment violations."""


def some_function(param_one,  # Bad: hanging indent
    param_two,
    param_three):
    return param_one + param_two + param_three


result = some_function(100,
    200,
    300
    )


chained = (df
           .filter(condition)
           .groupby(col))


formula = (price * quantity + tax
           - discount + shipping)


message = ("Lorem ipsum dolor sit amet "
           "consectetur adipiscing elit")


if (condition_one and
    condition_two or
    condition_three):
    pass


value = condition_one \
        and condition_two


config = {host: "localhost",
          port: 8080,
          debug: False,
          }