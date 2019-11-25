from django.core.exceptions import ValidationError


def validate_positive_float(value):

    """to validate a float is positive or raise validation error"""

    if value >= 0:
        return value
    return ValidationError("This field cannot be negative")


def validate_non_zero_positive_float(value):

    """to validate a float is positive or raise validation error"""

    if value > 0:
        print(value)
        return value
    return ValidationError("This field cannot be negative")
