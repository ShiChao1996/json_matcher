# coding:utf-8
"""
@time: 2021/1/9 5:24 下午
@author: shichao
"""
from json_matcher.matcher import JsonMatcher
from json_matcher.rule import or_, get_, all_, any_


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
    assert ok

    # =========case2=========
    data2 = {
        "a": 2,
        "b": {
            "bb": 2
        },
        "c": 123
    }
    ok, msg = matcher.is_match(data2)
    assert not ok
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
    assert not ok
    # False, "Type error, expect type: <class 'list'>, but get <class 'int'>"


def test_list():
    # =========case1=========
    tpl = {
        "a": 1,
        "b": [
            {
                "c": 1
            }
        ]
    }
    matcher = JsonMatcher(tpl)

    data1 = {
        "a": 1,
        "b": [
            1,
            {"c": 1},
            []
        ]
    }
    ok, msg = matcher.is_match(data1)
    assert ok
    # True, ""

    # =========case2=========
    tpl = {
        "a": 1,
        "b": [
            all_({
                "c": 1
            })
        ]
    }
    matcher = JsonMatcher(tpl)

    data1 = {
        "a": 1,
        "b": [
            1,
            {"c": 1},
            []
        ]
    }
    ok, msg = matcher.is_match(data1)
    assert not ok
    # False, None of element in list match the rule, detail:
    #   Type error, expect type: dict, but get <class 'int'>


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
    assert ok
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
    assert ok
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
    assert not ok
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
    assert ok
    # True, ""


def test_fetch():
    tpl = {
        "a": {
            "b": 1,
            "c": any_,
            "d": get_()
        }
    }

    matcher = JsonMatcher(tpl)
    data = {
        "a": {
            "b": 1,
            "c": {
                "c1": 1,
                "c2": [1, 2, 3]
            },
            "d": "xxx"
        },
    }

    ok, msg = matcher.is_match(data)
    assert ok
    fetch_data = matcher.get_data()
    assert fetch_data[0][0].get("d") == 'xxx'
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
    fetched_data = matcher.get_data()
    assert fetched_data[0][0].get("c") == 'data to fetch'


def test():
    tpl = {
        "?a": 1,
        "b": [
            all_({
                "?c": get_(),
                "?d": get_(),
            })
        ]
    }
    data = {
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
                "cc": 333,
                "d": 333
            },
        ]
    }
    matcher = JsonMatcher(tpl)
    # matcher.find_from_json(data)
    ok, msg = matcher.is_match(data)
    print(ok, msg)
    res = matcher.get_data()
    assert len(res) == 3
    assert res[2][0].get("d") == 333
    print(res)
