# coding:utf-8
"""
@time: 2021/1/9 5:24 下午
@author: shichao
"""
from json_matcher.matcher import JsonMatcher

if __name__ == "__main__":
    tpl = {
        "columns": [
            any_({
                "a": 1
            })
        ]
    }

    data = {
        "aaa": 1,
        "columns": [
            {
                "b": 1,
                "a": 1
            }
        ]
    }

    checker = JsonMatcher(tpl)
    ok, msg = checker.is_match(data)
    print(ok, msg)


class A():
    def __init__(self, *args):
        print(args)


a = A({"a": 1}, 2, 3)
