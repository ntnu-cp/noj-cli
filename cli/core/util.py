from typing import Generator, Iterable, List, TypeVar

T = TypeVar('T')


def chunker_list(
    seq: Iterable[T],
    size: int,
) -> Generator[List[T], None, None]:
    seq = iter(seq)
    while True:
        ret = []
        try:
            ret.extend(next(seq) for _ in range(size))
        except RuntimeError as e:
            assert 'StopIteration' in str(e)
            yield ret
            break
        yield ret
