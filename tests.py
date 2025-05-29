# -*- coding: utf-8 -*-
"""
    tests.py
"""
from __future__ import annotations

import dataclasses
import functools
import platform
import typing
from typing import List

import colorama

from timer import exec_times
from strs import fitlength, colorize
from iterable import get_dims


@dataclasses.dataclass
class BaseFuncTestcase:
    __EVAL_RESULT_TEXTS__ = {
        True: colorize('PASSED', colorama.Fore.GREEN),
        False: colorize('FAILED', colorama.Fore.RED)
    }

    @property
    def func_args(self):
        return dataclasses.astuple(self)[0]

    @property
    def _expected_func_return(self):
        return dataclasses.astuple(self)[1]
        
    def test(self, func_return):
        return func_return == self._expected_func_return

    def func_test_result_text(self, func_return):
        return self.__EVAL_RESULT_TEXTS__[self.test(func_return)]
    
    def print_func_return_test_result(self, func, func_return, print_values=True, return_text_maxlen=200):
        if isinstance(func, functools.partial):
            qualified_name = f'{func.func.__module__}.{func.func.__name__}'
        else:
            qualified_name = f'{func.__module__}.{func.__name__}'
        print(f' - [{self.__EVAL_RESULT_TEXTS__[self.test(func_return)]}] {qualified_name}')
        if print_values:
            print(f' - Expected: {fitlength(self._expected_func_return, maxlen=return_text_maxlen)}')
            print(f' - Return  : {fitlength(func_return, maxlen=return_text_maxlen)}')
            print()

    def print_test_result(self, func, print_values=True, return_text_maxlen=200):
        func_return = func(*self.func_args)
        self.print_func_return_test_result(func, func_return, print_values=print_values, return_text_maxlen=return_text_maxlen)

    def formatted_args(self, value_maxlen=200) -> List[str]:
        def format_value(value) -> str:
            if isinstance(value, int):
                text = format(value, ',d')
            else:
                text = str(value)

            dims = get_dims(value)
            if len(dims) > 0:
                dims_text = ' x '.join(map(str, dims))
                text = f'[dims: {dims_text}] {text}'

            return text
        
        EXPECTED_NAME = '[Expected]'

        attributes = [(attrname, value) for attrname, value in dataclasses.asdict(getattr(self, dataclasses.fields(self)[0].name)).items()]
        max_name_length = max(*map(len, list(zip(*attributes))[0]), len(EXPECTED_NAME))
        args = []
        for attrname, value in attributes:
            args.append((format(attrname, f'{max_name_length}s'), fitlength(format_value(value), maxlen=value_maxlen)))

        return (args, (format(EXPECTED_NAME, f'{max_name_length}s'), fitlength(format_value(getattr(self, dataclasses.fields(self)[1].name)), maxlen=value_maxlen)))
    
    def print_args(self, value_maxlen=200) -> None:
        print('* [Arguments] *')
        for name, value in self.formatted_args(value_maxlen)[0]:
            print(f'- {name}\t{value}')
        print('* {}\t{}'.format(*self.formatted_args(value_maxlen)[1]))

def descriptor(desc):
    def descriptor_adder(func):
        func.__description__ = desc
        return func

    return descriptor_adder

def python_implemntation_text() -> str:
    return f'{platform.python_implementation()} {platform.python_version()} revision {platform.python_revision()}'

def prepare_testcases(testcases: typing.Tuple[BaseFuncTestcase | typing.Tuple[typing.Tuple[typing.Any, ...], typing.Any]]) -> typing.Tuple[BaseFuncTestcase, typing.Any]:
    """Converts :testcases: to a tuple of a testcase data class.

    If a testcase is an instance of a descendent of BaseFuncTestcase, type of the instance encountered first will be used as the data class.
    otherwise, a new appropriate data class will be created and used.
    """
    if len(testcases) > 0:
        for testcase in testcases:
            if isinstance(testcase, BaseFuncTestcase):
                funcargs_class = type(testcase.func_args)
                testcase_class = type(testcase)
                print(f'Using an existing testcase data class: {type(testcase).__qualname__}')
                break
        else:
            funcargs_class = dataclasses.make_dataclass('FuncArgs', [(f'attr{index}', type(arg)) for index, arg in enumerate(testcase[0])])
            testcase_class = dataclasses.make_dataclass('FuncTestcase', [('args', funcargs_class), ('expected', type(testcase[1]))], bases=(BaseFuncTestcase,))
            print(f'Created new testcase data class: {testcase_class.__qualname__}')

    return [testcase if isinstance(testcase, BaseFuncTestcase) else testcase_class(funcargs_class(*testcase[0]),testcase[1]) for testcase in testcases]

def run_funcs_testcases(funcs: tuple[typing.Callable] | typing.Callable, testcases: typing.Tuple[BaseFuncTestcase | typing.Tuple[typing.Tuple[typing.Any, ...], typing.Any]], return_text_maxlen: int = 200):
    testcases = prepare_testcases(testcases)

    print()
    print(f'Python Implementation: {python_implemntation_text()}')
    print()
    for case, testcase in enumerate(testcases, start=1):
        print(f'----- Test Case {case} -----')
        testcase.print_args()
        print()

        try:
            iter(funcs)
            for func in funcs:
                testcase.print_test_result(func, return_text_maxlen=return_text_maxlen)
        except TypeError:
            testcase.print_test_result(funcs, return_text_maxlen=return_text_maxlen)
        
        print()

def time_funcs_testcases(funcs: tuple[typing.Callable] | typing.Callable, testcases: typing.Tuple[BaseFuncTestcase | typing.Tuple[typing.Tuple[typing.Any, ...], typing.Any]], repeats: int = 1, default_repeats: int = 1, return_text_maxlen: int = 200):
    """
    Args:
        funcs: A list/tuple of functions to tess.
        testcases: A list/tuple of testcases.
        runcasese: A dictionary of (testcase index: repeats)
            repeats: Number of repeated runs.

    Note:
    - If the type of repeats is int:
      - All test will be run for repeats number of times.
      - default_repeats argument is ignored.
    - If the type of repeats is dict:
      - If runcases has an entry for a testcase, it will be run for the specified repeats.
      - If runcases has an entry for a testcase and it is 0, the testcase will be skipped.
      - If runcases does not have an entry for a testcase, it will be run for default_repeats number of times.
    """
    testcases = prepare_testcases(testcases)

    print()
    print(f'Python Implementation: {python_implemntation_text()}')
    print()

    runcase = 1
    for testcase_index, testcase in enumerate(testcases):
        if isinstance(repeats, int):
            runcase_repeats = repeats
        elif isinstance(repeats, dict):
            runcase_repeats = repeats.get(testcase_index, None)
            if runcase_repeats is None:
                runcase_repeats = default_repeats
            elif runcase_repeats == 0:
                # If runcase repeats is 0, skip this testcase.
                continue
        else:
            raise TypeError(f'Type of repeats argument must be either int or dict. (Given: {type(repeats)})')
        
        print(f'----- Run Case [{runcase}]: Test Case [{testcase_index}] x {runcase_repeats:,} iterations -----')
        testcase.print_args()
        print()
        
        times = exec_times(funcs, *testcase.func_args, repeats=runcase_repeats)
        times.print_summary({func: testcase.func_test_result_text(func_return) for func, (func_return, _) in times._times.items()})
        print()

        runcase += 1
