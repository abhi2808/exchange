from itertools import groupby
from operator import itemgetter

__all__ = ['Filter', 'Report', 'grouping', 'subtotal', 'misra',]

import csv
import re

def __grouping(unsorted: tuple, indexes: tuple) -> dict:
    if len(indexes) == 0:
        return unsorted
    else:
        grouped = {}
        key = itemgetter(indexes[0])
        for k, v in groupby(sorted(unsorted, key=key), key=key):
            grouped[k] = __grouping(list(v), indexes[1:])
        return grouped


def grouping(data: tuple, indexes: list) -> dict:
    return __grouping(data, indexes)


def __subtotal(values, idx_value: int, depth: int = None):
    if isinstance(values, list) or isinstance(values, tuple):
        sum_value = 0
        for record in values:
            if Filter.is_int(str(record[idx_value])) is True:
                sum_value += int(record[idx_value])
            else:
                sum_value += float(record[idx_value])
        return sum_value, None
    elif depth is not None and depth == 0:
        sum_value = 0
        for k in values:
            ret = __subtotal(values[k], idx_value, depth)
            sum_value += ret[0]
        return sum_value, None
    else:
        if depth is not None:
            depth -= 1
        sum_value = 0
        ret = {}
        for k in values:
            ret[k] = __subtotal(values[k], idx_value, depth)
            sum_value += ret[k][0]
        return sum_value, ret


def subtotal(data: dict, idx_value: int, depth: int = None):
    return __subtotal(data, idx_value, depth)


def __subtotal2(values, idx_value: int, idx_covered: int, idx_cases: int, depth: int = None):
    if isinstance(values, list) or isinstance(values, tuple):
        sum_value = 0
        sum_covered = 0
        sum_cases = 0
        for record in values:
            if record[2] == 'Complexity':
                sum_value += int(record[idx_value])
            else:
                sum_covered += int(record[idx_covered])
                sum_cases += int(record[idx_cases])
        return sum_value, sum_covered, sum_cases, None
    elif depth is not None and depth == 0:
        sum_value = 0
        sum_covered = 0
        sum_cases = 0
        for k in values:
            ret = __subtotal2(values[k], idx_value, depth)
            sum_value += ret[0]
            sum_covered += ret[1]
            sum_cases += ret[2]
        return sum_value, sum_covered, sum_cases
    else:
        if depth is not None:
            depth -= 1
        ret = {}
        for k in values:
            ret[k] = __subtotal2(values[k], idx_value, idx_covered, idx_cases, depth)
        return ret


def subtotal2(data: dict, idx_value: int, idx_covered: int, idx_cases: int, depth: int = None):
    return __subtotal2(data, idx_value, idx_covered, idx_cases, depth)


class Filter:
    __instance = None

    def __init__(self):
        self.__filter = {}
        self.__iter = None

    @classmethod
    def builder(cls) -> 'Filter':
        if cls.__instance is None :
            cls.__instance = Filter()
        return cls

    @classmethod
    def put(cls, arg: str, value) -> 'Filter':
        this = cls.__instance
        if not this.__filter.__contains__(arg):
            this.__filter[arg] = []
        this.__filter[arg].append(value)
        return cls

    @classmethod
    def put_str(cls, arg: str, value) -> 'Filter':
        this = cls.__instance
        if not this.__filter.__contains__(arg):
            this.__filter[arg] = []
        this.__filter[arg].append(str(value))
        return cls

    @classmethod
    def build(cls) -> 'Filter':
        this = cls.__instance
        cls.__instance = None
        return this

    def __iter__(self):
        self.__iter = self.__filter.__iter__()
        return self

    def __next__(self) -> (str, []):
        k = self.__iter.__next__()
        v = self.__filter[k]

        return k, v

    @classmethod
    def is_int(cls, arg: str):
        try:
            int(arg)
            return True
        except ValueError:
            return False

class Report:
    def __init__(self, source_path: str, raw_filter: Filter = None):
        with open(source_path) as f:
            reader = csv.reader(f)

            self._idx = {}
            self._header = tuple(reader.__next__())
            for idx in range(len(self._header)):
                self._idx[self._header[idx]] = idx
                exec('self._idx_%s = %d' % (self._header[idx], idx))

            self._raw = []

            for row in reader:
                if raw_filter is not None:
                    is_hit = True
                    for key, filter_value in raw_filter:
                        value = row[self._header.index(key)]
                        if value not in filter_value:
                            is_hit = False
                            break
                    if not is_hit:
                        continue

                self._raw.append(tuple(row))

            self._raw = tuple(self._raw)

    def get_header(self) -> tuple:
        return self._header

    def get_body(self) -> tuple:
        return self._raw
