## JsonMatcher
这是一个方便易用的 Json 匹配工具，你可以使用熟悉的 Json 格式去表示你的匹配模板。并且提供了一个方法获取你想要的 value

### 基本概念
* 模板(template), 是你定义的 Json 匹配模板，模板可以嵌套
* 规则(rule), 通过模板解析出对应的规则，由于模板是嵌套的，所以规则也是嵌套的。
例如 **{"a": 1}** 代表2条规则，1-数据的类型是 dict, 2-dict 里有 key="a" 且 value=1
* 内置对象，工具内提供了特定的对象
    * and_: 当你有多个规则，你需要多个规则同时满足，可以用 any_, 用法如：any_(template1, template2)。
    当然多个规则共存的时候，默认是使用 and_ 的逻辑，因此大多数case可以省略
    * or_: 当你有多个规则，想要数据满足任何一条都可以通过
    * all_: 这个对象比较特殊，只用于 list 类型的模板里。list 类型的模板在默认情况下，只要有任意一条数据满足规则，那么这条规则就算匹配通过。
    当然你可以通过 all_ 对象指定当 list 数据的每一个元素都满足规则，才判定该规则匹配通过。具体的例子见基本用法。
    * any_: 这个名字和上面的 all_ 每一任何关系，它通常用于表示可以匹配任意类型的 value

### 基本用法
#### 基本模板匹配
```python
from json_matcher.matcher import JsonMatcher

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
```

另外，可以在模板的 key 前面加上 "?" 来表示这是一条可选的规则。含义为对应的数据可以不存在，但是如果存在，必须满足规则
#### List 模板

```python
from json_matcher.rule import all_
from json_matcher.matcher import JsonMatcher

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
    print(ok, msg)
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
    print(ok, msg)
    # False, None of element in list match the rule, detail: 
    #   Type error, expect type: dict, but get <class 'int'>
```
在上面的case1中，list 模板下只有一条规则，默认情况下数据里任意一条符合这个规则，那么久认为数据是符合条件的
在case2中，list 模板下也只有一条规则，但是是用 all_ 对象装饰的，这种模式下，必须要数据里每一个元素都满足规则，才认为数据是符合条件的

#### 逻辑匹配
**你可以在模板中使用 and_ 和 or_ 来表示 "与" 和 "或" 的匹配模式**
```python
from json_matcher import or_
from json_matcher.matcher import JsonMatcher

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
```

#### Fetch data
> JsonMatcher 还提供了一种途径让你获取指定的数据，但前提是整个数据符合了模板里的其他所有规则
```python
from json_matcher import get_
from json_matcher.matcher import JsonMatcher
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
```

#### Find and fetch
> check is there any part of a json matches a template, and support fetch data  

```python
from json_matcher.matcher import JsonMatcher
from json_matcher import get_
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
    matched_data = matcher.find_from_json(data)
    print(matched_data)
    # {'a': {'b': 1, 'c': 'data to fetch'}}
    fetched_data = matcher.get_data()
    print(fetched_data)
    # {'c': 'data to fetch'}
```

当在 List 模板里使用 get_ 的时候，一点需要注意的是，由于前面讲过的 List 模板的特性，
默认情况下当获取到第一条符合条件的数据后就不会在继续匹配同一条规则了，
所有如果想要获取 list 数据中每一条符合 get_ 规则的数据，可以和 all_ 组合使用，如下：
```python
from json_matcher.matcher import JsonMatcher
from json_matcher.rule import get_, all_

def test_fetch():
    tpl = {
        "a": 1,
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
                "cc": 222,
                "d": 222
            },
        ]
    }
    matcher = JsonMatcher(tpl)
    matcher.find_from_json(data)
    res = matcher.get_data()
    for item in res:
        print(item)
    #[{'c': 111}, {'d': 111}]
    #[{'c': 222}]
    #[{'d': 222}]
```
