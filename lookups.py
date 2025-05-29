# -*- coding: utf-8 -*-
"""
    lookups.py
"""
from __future__ import annotations

import enum
from numbers import Number
import typing


EqualitySideType = enum.Enum('EqualitySideType', ['Neither', 'Left', 'Right', 'Both'])

class IntervalMap:
    Equality = EqualitySideType

    def __init__(self, intervals_map: dict[tuple[Number, Number], typing.Any], default: typing.Optional[typing.Any] = None, equality: EqualitySideType = EqualitySideType.Left) -> None:
        """
        Args:
            :intervals_map: A dictionary of {range: value}
                :range: is a tuple of two numbers indicating range.
                    if range[0] is None, lower bound is assumed unbounded.
                    if range[1] is None or is not given, upper bound is assumed unbounded.
            :equal_left: indicates where the equality should be tested.
                if :equal_left: is True, than equality is tested to lower bound.
                otherwise,, than equality is tested to upper bound.

        Examples:
            :intervals_map: = dict(
                (2.0,): 'a'
                (1.0, 2.0): 'b'
                (0.0, 1.0): 'b'
                (None, 0.0): 'd'
            )
        """
        self._map = intervals_map.copy()
        for interval, value in list(self._map.items()):
            if interval[0] is None:
                del self._map[interval]
                self._map[(float('-inf'), interval[-1])] = value
            elif (len(interval) == 1) or (interval[1] is None):
                del self._map[interval]
                self._map[(interval[0], float('inf'))] = value

        self._default = default
        self._equality = equality

    def lookup(self, lookup_value: typing.Any) -> typing.Any:
        """
        Args:
            :value: 

        Examples:
            :intervals_map: = dict(
                (2.0,): 'a'
                (1.0, 2.0): 'b'
                (0.0, 1.0): 'b'
                (None, 0.0): 'd'
            )
            interval_match(:intervals_map:, equal_left=True)
        """
        def lower_bound_test(bound):
            return bound < lookup_value if (bound > float('-inf')) and (self._equality not in (EqualitySideType.Left, EqualitySideType.Both)) else bound <= lookup_value
        
        def upper_bound_test(bound):
            return lookup_value < bound if (bound < float('inf')) and (self._equality in (EqualitySideType.Left, EqualitySideType.Neither)) else lookup_value <= bound
        
        for (lower_bound, upper_bound), mapped in self._map.items():
            if lower_bound_test(lower_bound) and upper_bound_test(upper_bound):
                return mapped
        
        return self._default


ThresholdType = enum.Enum('BoundType', ['LowerBound', 'UpperBound'])

class ThresholdMap(IntervalMap):
    Boundary = ThresholdType

    def __init__(self, thresholds_map: dict[Number, typing.Any], default: typing.Optional[typing.Any] = None, threshold_type: ThresholdType = ThresholdType.LowerBound) -> None:
        """
        Args:
            :intervals_map: A dictionary of {threshold: value}
                :range: is a tuple of two numbers indicating range.
                    if range[0] is None, lower bound is assumed unbounded.
                    if range[1] is None or is not given, upper bound is assumed unbounded.
            :equal_left: indicates where the equality should be tested.
                if :equal_left: is True, than equality is tested to lower bound.
                otherwise,, than equality is tested to upper bound.

        Examples:
            :intervals_map: = dict(
                2.0: 'a'
                1.0: 'b'
                0.0: 'b'
            )
        """
        if threshold_type not in [v for v in ThresholdType]:
            raise ValueError(f'Invalid threshold boundary type: {threshold_type}; must be among {[str(v) for v in ThresholdType]}')

        bounds = tuple(sorted(thresholds_map.items(), key=lambda t: t[0]))
        items = []
        for lower, upper in zip(bounds, bounds[1:]):
            if threshold_type == ThresholdType.LowerBound:
                items.append(((lower[0], upper[0]), lower[1]))
            elif threshold_type == ThresholdType.UpperBound:
                items.append(((lower[0], upper[0]), upper[1]))

        map_ = dict(items)
        if threshold_type == ThresholdType.LowerBound:
            map_[(bounds[-1][0],)] = bounds[-1][1]
        elif threshold_type == ThresholdType.UpperBound:
            map_[(None, bounds[0][0],)] = bounds[0][1]

        super().__init__(map_, default, equality=IntervalMap.Equality.Left if threshold_type == ThresholdType.LowerBound else IntervalMap.Equality.Right)
