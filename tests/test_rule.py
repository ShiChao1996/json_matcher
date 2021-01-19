# coding:utf-8
"""
@time: 2021/1/17 12:09 上午
@author: shichao
"""
from json_matcher.rule import all_, get_, rf


def test_basic():
    tpl = {
        "a": 1,
        "b": [
            all_({
                "?c": get_(),
                "?d": get_(),
            })
        ]
    }
    rule = rf.gen_rule(None, "", tpl)
    rule.try_match({
        "a": 1,
        "b": [
            {
                "c": 111,
                "d": 111
            },
            {
                "c": 222,
                "dd": 222
            },
            {
                "cc": 222,
                "d": 222
            },
        ]
    })
    data = rule.combine_data()
    for item in data:
        print(item)

    tpl = {
        "a": 1
    }
    rules = rf.gen_rule(None, "", tpl)
    rules.match({
        "a": 1
    })

    # ==============
    tpl = {
        "a": {
            "b": 1
        }
    }
    rules = rf.gen_rule(None, "", tpl)
    rules.match({
        "a": {
            "b": 1
        }
    })

    # ==============
    tpl = {
        "a": {
            "b": {
                "c": 1
            }
        }
    }
    rules = rf.gen_rule(None, "", tpl)
    rules.match({
        "a": {
            "cc": "",
            "b": {
                "aa": 1,
                "c": 1
            }
        }
    })
