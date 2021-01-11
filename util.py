# coding:utf-8
"""
@time: 2021/1/11 11:06 上午
@author: shichao
"""


def labels(cls):
    """
    枚举的labels定义
    :param cls:
    :return:
    """

    def to_str(types, val):
        """
        labels转换
        :param types:
        :param val:
        :return:
        """
        if hasattr(types, "__labels__"):
            return types.__labels__.get(int(val))
        return val

    cls.label = classmethod(to_str)
    return cls
