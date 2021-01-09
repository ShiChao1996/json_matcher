# coding:utf-8
"""
@time: 2021/1/9 5:24 下午
@author: shichao
"""
from json_matcher.matcher import JsonChecker

if __name__ == "__main__":
    tpl = {
        "columns": [
            {
                "a": 1
            }
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

    checker = JsonChecker(tpl)
    print(checker.check_rule(data))
