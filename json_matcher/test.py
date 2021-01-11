# coding:utf-8
"""
@time: 2021/1/9 5:24 下午
@author: shichao
"""
from json_matcher.matcher import JsonMatcher
from json_matcher.rule import or_, get_


def test_basic():
    tpl = {
        "a": 1,
        "b": {
            "bb": 2
        },
        "c": list
    }
    matcher = JsonMatcher(tpl)

    # =========case1=========
    data1 = {
        "a": 1,
        "b": {
            "bb": 2
        },
        "c": [1, 2, 3]
    }
    ok, msg = matcher.is_match(data1)
    print(ok, msg)
    # True, ""

    # =========case2=========
    data2 = {
        "a": 2,
        "b": {
            "bb": 2
        },
        "c": 123
    }
    ok, msg = matcher.is_match(data2)
    print(ok, msg)
    # False, "Value error a, expect 1, but get 2"

    # =========case3=========
    data3 = {
        "a": 1,
        "b": {
            "bb": 2
        },
        "c": 123
    }
    ok, msg = matcher.is_match(data3)
    print(ok, msg)
    # False, "Type error, expect type: <class 'list'>, but get <class 'int'>"


def test_logic():
    tpl = {
        "a": [
            1, 2
        ],
        "b": {
            "bb": 1
        }
    }
    matcher = JsonMatcher(tpl)

    # =========case1=========
    data1 = {
        "a": [
            1, 2, 3, 4
        ],
        "b": {
            "bb": 1
        },
    }
    ok, msg = matcher.is_match(data1)
    print(ok, msg)
    # True, ""
    # Note：for each rule in list template, if any element in data matches the rule, will return true

    # =========case2=========
    tpl = {
        "a": [
            1, 2
        ],
        "b": {
            "bb": 1
        },
        "c": or_(1, 2)
    }
    matcher = JsonMatcher(tpl)
    data2 = {
        "a": [
            1, 2, 3, 4
        ],
        "b": {
            "bb": 1
        },
        "c": 1
    }
    ok, msg = matcher.is_match(data2)
    print(ok, msg)
    # True, ""

    data3 = {
        "a": [
            1, 2, 3, 4
        ],
        "b": {
            "bb": 1
        },
        "c": 3
    }
    ok, msg = matcher.is_match(data3)
    print(ok, msg)
    # False Value error logic_op_or, expect 1, but get 3
    # Value error logic_op_or, expect 2, but get 3

    # =========case3=========
    tpl = {
        "a": or_(
            {
                "b": 1
            },
            {
                "c": 1
            }
        )
    }
    matcher = JsonMatcher(tpl)
    data4 = {
        "a": {
            "b": 1,
            "bb": 2,
            "bbb": 3,
            "bbbb": {
                "c": 1,
                "cc": 2
            }
        },
        "b": []
    }
    ok, msg = matcher.is_match(data4)
    print(ok, msg)
    # True, ""


def test_fetch():
    tpl = {
        "a": {
            "b": 1,
            "c": get_()
        }
    }

    matcher = JsonMatcher(tpl)
    data = {
        "abc": [1, 2, 3],
        "a": {
            "b": 1,
            "c": {
                "c1": 1,
                "c2": [1, 2, 3]
            },
            "d": "xxx"
        },
        "bac": {1, 2, 3}
    }

    ok, msg = matcher.is_match(data)
    print(ok, msg)
    # True, ""
    fetch_data = matcher.get_data()
    print(fetch_data)
    # {'c': {'c1': 1, 'c2': [1, 2, 3]}}


def test_parse():
    tpl = {
        "a": {
            "b": 1,
            "c": get_()
        }
    }

    data = {
        "key1": "val1",
        "key2": {
            "a": {
                "b": 1,
                "c": "data to fetch"
            }
        },
        "key3": []
    }
    matcher = JsonMatcher(tpl)
    matched_data = matcher._find_from(data)
    print(matched_data)
    # {'a': {'b': 1, 'c': 'data to fetch'}}
    fetched_data = matcher.get_data()
    print(fetched_data)
    # {'c': 'data to fetch'}


if __name__ == "__main__":
    # test_basic()
    # test_logic()
    # test_fetch()
    test_parse()
