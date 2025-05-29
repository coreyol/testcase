# -*- coding: utf-8 -*-
"""
    leetcode_00075.py

    Leetcode 75: Sort Colors
    https://leetcode.com/problems/sort-colors/
"""

import typing

# ---------- Reference function - brute force method ---------- #

def reference_func(nums: list[int]) -> None:
    return sorted(nums)

# ---------- Reference function - brute force method ---------- #

# ---------- counter ---------- #

def sortColors_counter(nums: list[int]) -> None:
    sortColors_counter.__description__ = 'counter'

    counter = dict()
    for num in nums:
        counter.setdefault(num, 0)
        counter[num] += 1

    sorted_nums = [0] * len(nums)
    index = 0
    for color in sorted(counter.keys()):
        for _ in range(counter[color]):
            sorted_nums[index] = color
            index += 1

    return sorted_nums

# ---------- counter ---------- #

# ---------- tow pointer ---------- #

def sortColors_two_pointer(nums: list[int]) -> None:
    sortColors_two_pointer.__description__ = 'two pointer'

    sorted_nums = nums.copy()
    swap_target = 0
    for color in (0, 1, 2)[:-1]:
        color_position = len(nums) - 1
        while (swap_target < color_position):
            while (swap_target < color_position) and (sorted_nums[swap_target] == color):
                swap_target += 1

            while (swap_target < color_position) and (sorted_nums[color_position] != color):
                color_position -= 1

            if swap_target < color_position:
                sorted_nums[swap_target], sorted_nums[color_position] = sorted_nums[color_position], sorted_nums[swap_target]

    return sorted_nums

# ---------- tow pointer ---------- #




if __name__ == '__main__':
    import random
    import math
    import enum
    import typing

    from tests import time_funcs_testcases
    from tests import run_funcs_testcases

    from strs import fitlength
    from iterable import get_dims

    TestcaseArgsType = tuple[list[int]] # (nums: list[int],)
    ExpectedReturnType = None
    GenerationParamsType = dict[str, typing.Any] # dict(seed_range: tuple[int, int], )
    GeneratorInternalParamsType = dict[str, typing.Any] # dict()
    
    def fill_testcases(ref_func: typing.Callable, n_testcases: int, initial_seed: int, **generation_params: GenerationParamsType) -> None:
        """
            Modify the return of generate_func_arguments_set accordingly.
        """
        def arg_text(value: typing.Any, max_len: int, format_spec: typing.Optional[str] = None) -> str:
            dims = get_dims(value)
            dims_text = '' if len(dims) == 0 else f'[dims: {" x ".join(map(str, dims))}] '
            
            return dims_text + fitlength(format_spec.format(value) if format_spec is not None else str(value), max_len)
        
        def generate_func_arguments_set(generation_params: GenerationParamsType) -> list[typing.Any]:
            """
                Must return: A tuple of (label, argumemt, format_spec or None),
                    in the same order as function arguments to the test case generator.
            """
            class Bundle:
                def __init__(self, adict):
                    self.__dict__.update(adict)

            params = Bundle(generation_params)
            return (
                ('seed', random.randint(*params.seed_range), None),
            )

        value_max_len = 200

        print(f'Generating {n_testcases} test cases...')
        n_testcases_len = int(math.log10(n_testcases)) + 1 if n_testcases > 0 else 0
        random.seed(initial_seed)
        params = [generate_func_arguments_set(generation_params) for _ in range(n_testcases)]
        for index, generator_args_set in enumerate(params, start=1):
            generator_args_str = ', '.join(f'{label}: {value:{fmt_spec if fmt_spec is not None else ""}}' for label, value, fmt_spec in generator_args_set)
            print(f'[{index:>{n_testcases_len}}] {generator_args_str}')
            args, internal_params = generate_testcase(*(arg for _, arg, _ in generator_args_set))
            internal_params_str = ', '.join([f'{label}: {value}' for label, value in internal_params.items()])
            if len(internal_params_str) > 0:
                print(f'[{index:>{n_testcases_len}}] {internal_params_str}')
            args_text = ', '.join([arg_text(arg, value_max_len) for arg in args])
            print(f'[{index:>{n_testcases_len}}] Arguments: {args_text}')
            result = ref_func(*args)
            print(f'[{index:>{n_testcases_len}}] Expected: {arg_text(result, value_max_len)}')
            test_cases.append((args, result))
            print()

    # ---------- Handpicked testcases ---------- #
    
    def manual_testcase() -> TestcaseArgsType:
        return
    
    def manual_testcase_expected() -> tuple[TestcaseArgsType, ExpectedReturnType]:
        args = manual_testcase()
        expected = reference_func(*args)
        return (args, expected)

    test_cases = [
        (([2, 0, 2, 1, 1, 0],), [0, 0, 1, 1, 2, 2]),
        (([2, 0, 1],), [0, 1, 2]),

        (([0, 0, 0, 0, 0],), [0, 0, 0, 0, 0]),
        (([1, 1, 1, 1, 1],), [1, 1, 1, 1, 1]),
        (([2, 2, 2, 2, 2],), [2, 2, 2, 2, 2]),

        (([2, 2, 2, 1, 1, 1, 0, 0, 0],), [0, 0, 0, 1, 1, 1, 2, 2, 2]),

    ]

    n_manual_testcases = len(test_cases)

    # ---------- Generated testcases ---------- #

    n_random_testcases = 0
    
    generator_parameters = dict(
        initial_seed = 38059403,
        seed_range = (1, 100000),
    )

    test_repeats = {
    }
    radom_testcasses_test_repeats = 5
    default_test_repeats = 10000

    test_repeats.update({
        n_manual_testcases + i: radom_testcasses_test_repeats for i in range(len(test_cases) - n_manual_testcases)
    })
    
    TestcaseMode = enum.Enum('TestcaseMode', ['Regular',])
    RunMode = enum.Enum('RunMode', ['RunningTimeComparison', 'IndividualTest'])

    test_mode = TestcaseMode.Regular
    run_mode = RunMode.RunningTimeComparison
    # run_mode = RunMode.IndividualTest

    funcs = (
        reference_func,
        sortColors_counter,
        sortColors_two_pointer,
    )

    range_funcs = (
    )

    fill_testcases(reference_func, n_random_testcases, **generator_parameters)

    def run_test(test_mode: TestcaseMode = TestcaseMode.Regular, run_mode: RunMode = RunMode.IndividualTest) -> None:
        match test_mode:
            case TestcaseMode.Regular:
                args = (funcs, test_cases)
                kwargs = dict(
                    repeats = test_repeats, 
                    default_repeats = default_test_repeats
                )

        match run_mode:
            case RunMode.RunningTimeComparison:
                time_funcs_testcases(*args, **kwargs)
            case RunMode.IndividualTest:
                run_funcs_testcases(*args)

    run_test(test_mode, run_mode)
