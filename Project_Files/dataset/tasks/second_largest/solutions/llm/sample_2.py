from typing import List, Optional, Union

Number = Union[int, float]


def second_largest(numbers: List[Number]) -> Number:
    """Return the second largest distinct value using a single pass.

    Two running trackers hold the largest and second-largest distinct
    values seen so far. Values equal to the current largest are skipped
    so repeats do not occupy the runner-up slot.
    """
    largest: Optional[Number] = None
    runner_up: Optional[Number] = None

    for value in numbers:
        if largest is None or value > largest:
            if largest is not None:
                runner_up = largest
            largest = value
        elif value != largest and (runner_up is None or value > runner_up):
            runner_up = value

    if runner_up is None:
        raise ValueError("list must contain at least two distinct values")
    return runner_up
