from typing import Iterable


def chunker_list(seq: Iterable, size: int):
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
