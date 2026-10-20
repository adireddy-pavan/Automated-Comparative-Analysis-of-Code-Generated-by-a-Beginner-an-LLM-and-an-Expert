from functools import reduce
from operator import add
from typing import List, Union

Number = Union[int, float]


def sum_list(numbers: List[Number]) -> Number:
    """Return the sum of ``numbers`` using a functional reduction.

    ``functools.reduce`` folds ``operator.add`` across the sequence with an
    initial value of ``0``, which also defines the result for the empty
    list.
    """
    return reduce(add, numbers, 0)
