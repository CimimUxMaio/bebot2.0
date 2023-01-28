from typing import TypeVar


T = TypeVar("T")


def group(_list: list[T], group_size: int) -> list[list[T]]:
    return [_list[i: i + group_size] for i in range(0, len(_list), group_size)]
