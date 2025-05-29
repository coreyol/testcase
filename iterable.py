# -*- coding: utf-8 -*-
"""
    iterable.py

(2023-11-24)
General-purpose classes and functions for manipulating iterables.
"""
import typing

def get_dims(value: typing.Any) -> list:
    """
    Returns: A list of dimensions of :value: (if any).
        [], if :value: is not iterable, or :value: does not have :value:[0].
        if value is str, returns [len(value),]
        However, for strings inside sequences, their lengths are not included;
        only the dimensions of the container structure is returend.
    """
    dims = []
    try:
        while True:
            # If string is encountered inside sequence
            if value[0] == value:
                break
            dims.append(len(value))
            value = value[0]
    except (TypeError, IndexError):
        pass

    return dims
