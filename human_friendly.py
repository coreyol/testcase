# -*- coding: utf-8 -*-
"""
    human_friendly.py
"""

def magnitude_orders(magnitude, multiple, units, decimals=2):
    """
    Human-friendly orders of manitude.

    Args:
        magnitude: magnitude
        multiple: 1000, 1024, etc.
        units: A list of units
        decimals: Maximum number of decimal points
    """
    assert multiple > 0

    for unit in units[:-1]:
        if abs(magnitude) < multiple:
            return f'{magnitude:,.{decimals}f} {unit}'
        magnitude /= multiple

    return f'{magnitude:,.{decimals}f} {units[-1]}'

def binary_size(magnitude, decimals=2):
    return magnitude_orders(magnitude, 1024, ('B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB'), decimals=decimals)

def seconds(secs: float, decimal_precision: int = 5) -> str:
    units = (
        (1, 'sec'),
        (1000, 'ms'),
        (1000, 'us'),
        (1000, 'ns'),
    )

    for divisor, unit in units:
        secs *= divisor
        if secs >= 1.0:
            return f'{secs:.{decimal_precision}} {unit}'
    else:
        return f'{secs:.{decimal_precision}} {unit}'
