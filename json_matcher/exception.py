# coding:utf-8
"""
@time: 2021/1/14 11:04 下午
@author: shichao
"""

from abc import abstractmethod
from enum import IntEnum


class RuleException(Exception):
    @abstractmethod
    def string(self) -> str:
        pass


class KeyException(RuleException):
    def __init__(self, key):
        self.key = key

    def string(self) -> str:
        return "Key error, key: {} does not exist"


class ValueCheckType(IntEnum):
    VALUE = 1
    VALUE_TYPE = 2


class ValueException(RuleException):
    def __init__(self, expect, data, check_type: ValueCheckType):
        self.expect = expect
        self.data = data
        self.check_type = check_type

    def string(self) -> str:
        fmt = "expect: {}, but get: {}".format(self.expect, self.data)
        prefix = ""
        if self.check_type == ValueCheckType.VALUE:
            prefix = "Value not match"
        elif self.check_type == ValueCheckType.VALUE_TYPE:
            prefix = "Value type not match"

        return "{}, {}".format(prefix, fmt)
