from typing import Iterable, List, Optional, Tuple


def two_sum(nums: List[int], target: int) -> Optional[Tuple[int, int]]:
    """Return the earliest index pair whose values sum to ``target``.

    Implemented functionally: build the running map of seen values and use
    ``next`` over a generator of valid matches to grab the first one,
    falling back to ``None`` when the generator is exhausted.
    """

    def _matches() -> Iterable[Tuple[int, int]]:
        seen: dict[int, int] = {}
        for index, value in enumerate(nums):
            partner = seen.get(target - value)
            if partner is not None:
                yield (partner, index)
            seen.setdefault(value, index)

    return next(iter(_matches()), None)
