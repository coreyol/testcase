# -*- coding: utf-8 -*-
"""
    timer.py
"""
from __future__ import annotations

import datetime
import time
import dataclasses
from collections import namedtuple
import functools
import gc

# For type hints
import typing

import colorama

from strs import colorize, append_lateral_lines
from lookups import ThresholdMap


class TimerError(Exception):
    pass


@dataclasses.dataclass(frozen=True)
class MonotonicElapsed:
    counter_ns: int
    end_counter_ns: typing.Union[int, None] = None

    @property
    def monotonic_elapsed_ns(self):
        if self.end_counter_ns is None:
            return self.counter_ns
        else:
            return self.end_counter_ns - self.counter_ns

    @property
    def monotonic_elapsed(self):
        return self.monotonic_elapsed_ns / 10**9

    @property
    def elapsed(self):
        return datetime.timedelta(microseconds=self.monotonic_elapsed_ns / 1000)

    @property
    def elapsed_seconds(self):
        return self.elapsed.total_seconds()

    @property
    def elapsed_seconds_sec(self):
        return f'{self.elapsed_seconds} sec'

    def text(self, msec_precision=9):
        return format_timespan_seconds(self.monotonic_elapsed, msec_precision=msec_precision)
    
    def __truediv__(self, other):
        return self.monotonic_elapsed_ns / other.monotonic_elapsed_ns

    def __str__(self):
        return self.text(msec_precision=9)
    
    def __eq__(self, other: MonotonicElapsed):
        return self.monotonic_elapsed_ns == other.monotonic_elapsed_ns
    
    def __lt__(self, other: MonotonicElapsed):
        return self.monotonic_elapsed_ns < other.monotonic_elapsed_ns
    
    def __gt__(self, other: MonotonicElapsed):
        return self.monotonic_elapsed_ns > other.monotonic_elapsed_ns
    
    def __le__(self, other: MonotonicElapsed):
        return self.monotonic_elapsed_ns <= other.monotonic_elapsed_ns
    
    def __ge__(self, other: MonotonicElapsed):
        return self.monotonic_elapsed_ns >= other.monotonic_elapsed_ns

class Elapsed(namedtuple('Elapsed', ['start_time', 'end_time'])):
    __DATETIME_TEXT_FORMAT__ = '%Y-%m-%d %H:%M:%S.%f'

    @property
    def start_time_str(self):
        return self.start_time.strftime(Elapsed.__DATETIME_TEXT_FORMAT__)

    @property
    def end_time_str(self):
        return self.end_time.strftime(Elapsed.__DATETIME_TEXT_FORMAT__)
    
    @property
    def elapsed(self):
        return self.end_time - self.start_time

    @property
    def elapsed_seconds(self):
        return self.elapsed.total_seconds()

    @property
    def elapsed_seconds_sec(self):
        return f'{self.elapsed_seconds} sec'

    def __str__(self):
        return format_timedelta(self.elapsed)

class MonotonicTimer():
    def __init__(self):
        super().__init__()
        
        self._start = None
        self._accum = 0

        self.reset()

    @property
    def stopped(self):
        return (self._start is None)
        
    def start(self):
        """
        Raises:
            TimerError, if timer has started already.
        """
        if not self.stopped:
            raise TimerError("Timer has started already.")

        self._start = time.perf_counter_ns()
        
    def pause(self):
        """
        Pauses timer. The time delta is accumulated.
        """
        if not self.stopped:
            end = time.perf_counter_ns()
            self._accum += abs(end - self._start)
            self._start = None

    def resume(self):
        if self.stopped:
            self._start = time.perf_counter_ns()
            
    def stop(self):
        """
        Stops timer. The time delta is accumulated.

        Raises:
            TimerError, if timer has stopped already.
        """
        if self.stopped:
            raise TimerError("Timer has not started yet.")

        end = time.perf_counter_ns()
        self._accum += abs(end - self._start)
        self._start = None
            
    def reset(self):
        self._start = None
        self._accum = 0
        
    def restart(self):
        """
        Restarts timer.
        """
        self.reset()
        self.start()
        
    @property
    def elapsed(self):
        """
        If timer is not stopped, returns timedelta upto current time and the timer keeps running.
        """
        if self.stopped:
            accum_elapsed = self._accum
        else:
            accum_elapsed = self._accum + abs(time.perf_counter_ns() - self._start_time)

        return MonotonicElapsed(accum_elapsed)


def format_timespan_seconds(timespan, msec_precision=0):
    """Formats timespan

    :param timespan: A float indicating the time span in seconds
    :return: Formatted string for td, in HH:MM:SS.XXX
    """
    days, timespan_24hr = divmod(timespan, 24 * 60 * 60)
    days_text = f'{days:,}d ' if days > 0 else ''
    if msec_precision > 0:
        return days_text + f'{int(timespan_24hr // 3600):02}:{int((timespan_24hr % 3600) // 60):02}:{int(timespan_24hr % 60):02}.{int(timespan_24hr * (10**9) % (10**9)):0{msec_precision}}'
    else:
        return days_text + f'{int(timespan_24hr // 3600):02}:{int((timespan_24hr % 3600) // 60):02}:{int(timespan_24hr % 60):02}'


class ExecTimes:
    # if ExecTimes.__BULLET__ is not None, it is prepended before each line of summary.
    __BULLET__ = '-'

    def __init__(self, repeats=1):
        self._times = {}
        self._repeats = repeats

    def add_exec_time(self, func, func_return, exec_time):
        self._times[func] = (func_return, exec_time)

    @property
    def bullet(self):
        return ExecTimes.__BULLET__.join([' ', ' ']) if ExecTimes.__BULLET__ is not None else ''
    
    @property
    def exec_times_sorted_funcs(self):
        return [func for func, _ in sorted(self._times.items(), key=lambda t: t[1][1])]
    
    @property
    def comparison_matrix(self):
        """
        speed = 1 / t
        ratio = speed - speed_ref = (1 / t) / (1 / t_ref) = t_ref / t
        """
        exec_times = [self._times[func][1] for func in self.exec_times_sorted_funcs]
        return [[exec_times[col] / exec_times[row] for col in range(len(exec_times))] for row in range(len(exec_times))]

    def formatted_comparison_matrix(self, self_symbol: tuple[str, str] = ('-', colorama.Fore.RESET), best_symbol: tuple[str, str] = ('+++', colorama.Fore.RESET), worst_symbol: tuple[str, str] = ('---', colorama.Fore.RESET), column_interspaces: int = 1):
        VALUE_COLORS = {
            # Defines lower bound for text color.
            2.0: colorama.Fore.LIGHTCYAN_EX,
            1.0: colorama.Fore.GREEN,
            float('-inf'): colorama.Fore.RED
        }

        def format_value(value: typing.Any, percentage_threshold: float = 2.0):
            """
            :percentage_threshold: if value < :percentage_threshold:, value will be displayed in percentage.
                Otherwise, value will be displayed as 'x :value:'.
            """
            multiple_symbol = 'x'
            text_with_color = (
                f'{value:,.2%}',
                text_color.lookup(value)
            ) if value < percentage_threshold else (
                f'{multiple_symbol}{value:,.2f}',
                lambda text: text[:text.find(multiple_symbol)] + colorize(text[text.find(multiple_symbol)], colorama.Fore.LIGHTBLACK_EX) + colorize(text[text.find(multiple_symbol) + 1:], text_color.lookup(value))
            )
            return text_with_color
        
        text_color = ThresholdMap(VALUE_COLORS, threshold_type=ThresholdMap.Boundary.LowerBound)
        mat = [[format_value(value) if i != j else self_symbol for j, value in enumerate(row)] for i, row in enumerate(self.comparison_matrix)]

        # Comparison matrix is already sorted in ascending order of execution time.
        mat[0][0] = best_symbol
        mat[len(mat) - 1][len(mat[0]) - 1] = worst_symbol
        column_widths = [max(map(lambda t: len(t[0]), column_texts)) for column_texts in zip(*mat)]
        for row in mat:
            for col, (text, color) in enumerate(row):
                formatted_text = f'{text:>{column_widths[col]}}'
                row[col] = colorize(formatted_text, color) if isinstance(color, str) else color(formatted_text)

        return [(' ' * column_interspaces).join(row) for row in mat]
    
    def summary(self, test_results: dict[typing.Callable, str]):
        def get_func(func):
            if isinstance(func, functools.partial):
                return func.func
            else:
                return func

        max_module_name_length = max(map(lambda f: len(get_func(f).__module__), self._times.keys()))
        max_func_name_length = max(map(lambda f: len(get_func(f).__name__), self._times.keys()))
        max_func_desc_length = max(map(lambda f: len(getattr(f, '__description__', '')), self._times.keys()))
        
        lines = [f'Execution times: (iterations: {self._repeats:,})']
        for func in self.exec_times_sorted_funcs:
            exec_time = self._times[func][1]
            desc = ''
            if max_func_desc_length > 0:
                desc = f'[{getattr(func, "__description__", ""):{max_func_desc_length}}] '
            func = get_func(func)
            lines.append(f'{self.bullet}{desc}{func.__module__:>{max_module_name_length}}.{func.__name__:{max_func_name_length}}: [{test_results[func]}] {exec_time}')

        best_symbol = ('Best', colorama.Fore.YELLOW)
        worst_symbol = ('Worst', colorama.Fore.BLACK)
        speed_ratio_lines = [
            'Cross-relative speed ratio',
            *self.formatted_comparison_matrix(best_symbol=best_symbol, worst_symbol=worst_symbol),
            'r_i,j = v_i / v_j = t_j / t_i',
        ]
        lines = append_lateral_lines(lines, 0, speed_ratio_lines)

        return lines

    def print_summary(self, test_results: dict[typing.Callable, str]):
        for line in self.summary(test_results):
            print(line)

def exec_times(funcs, *args, repeats=1):
    times = ExecTimes(repeats)

    for func in funcs:
        lru_cached_funcs = [obj for obj in gc.get_objects() if isinstance(obj, functools._lru_cache_wrapper)]
        message = f'Measuring {func.__module__}.{func.__name__} ...'
        print(message, end='')
        timer = MonotonicTimer()
        for _ in range(repeats):
            # If there are functions func is wrapped by functools.lru_cache, clear cache to ensure precise measurement for repeated runs.
            for obj in lru_cached_funcs:
                obj.cache_clear()

            timer.start()
            func_return = func(*args)
            timer.pause()

        print('\r' + ' ' * len(message) + '\r', end='')
        times.add_exec_time(func, func_return, timer.elapsed)
        
    return times
