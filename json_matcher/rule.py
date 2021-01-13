# coding:utf-8
"""
@time: 2021/1/10 3:24 下午
@author: shichao
"""
import typing
import uuid
from enum import IntEnum

from json_matcher.util import labels
from abc import abstractmethod

VALUE_FETCH_KEY_DEFAULT = "VALUE_FETCH_KEY_DEFAULT"
VALUE_FETCH_KEY_ALL = "VALUE_FETCH_KEY_ALL"


class TxMap:
    def __init__(self):
        self.data = {}

    def update(self, k, v):
        val = self.data.get(k, 0)
        if not val or val > v:
            val = v

        self.data[k] = val

    def clear(self):
        self.data = {}

    def get_by_key(self, k):
        return self.data.get(k, 0)

    def query_by_min_val(self, val):
        return [k for k, v in self.data.items() if v > val]


tx_map = TxMap()


class Rule:
    def __init__(self, parent, key=""):
        self._key = key
        self._parent = parent
        self._depth = 0
        if parent:
            self._depth = parent.depth + 1

    @property
    def optional(self):
        return self._key.startswith("?")

    @property
    def depth(self):
        return self._depth

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, p):
        self._parent = p
        if p:
            self._depth = p.depth + 1

    @abstractmethod
    def match(self, data):
        raise NotImplementedError

    def try_match(self, data):
        tx_keys = tx_map.query_by_min_val(self.depth)
        try:
            self.match(data)
        except AssertionError as e:
            for key in tx_keys:
                self.rollback_data(key)
            raise e

        for key in tx_keys:
            self.commit_data(key)

    def get_data(self):
        data = []
        if isinstance(self, ValueFetcher):
            data.extend(self.data)

        if isinstance(self, RuleWithChild):
            for sub_rule in self._children:
                sub_data = sub_rule.get_data()
                data.extend(sub_data)

        return data

    def combine_data(self):
        all_data = self.get_data()
        res = {}
        for item in all_data:
            for commit_no, data in item.items():
                val = res.get(commit_no, [])
                val.extend(data)
                if val:
                    res[commit_no] = val

        return res.values()

    def commit_data(self, tx_key=VALUE_FETCH_KEY_DEFAULT, commit_no=""):
        commit_no = commit_no or str(uuid.uuid4())
        if isinstance(self, ValueFetcher) and self.tx_key in (tx_key, VALUE_FETCH_KEY_ALL):
            self.commit(commit_no)

        if isinstance(self, RuleWithChild):
            for sub_rule in self._children:
                sub_rule.commit_data(tx_key, commit_no)

    def rollback_data(self, tx_key=""):
        if isinstance(self, ValueFetcher) and self.tx_key in (tx_key, VALUE_FETCH_KEY_ALL):
            self.rollback()

        if isinstance(self, RuleWithChild):
            for sub_rule in self._children:
                sub_rule.rollback_data(tx_key)


class ValueFetcher(Rule):
    def __init__(self, parent=None, tx_key=VALUE_FETCH_KEY_DEFAULT):
        self.tx_key = tx_key
        self.data = []
        self.temp_data = []
        super(ValueFetcher, self).__init__(parent)

    def match(self, data):
        self.fetch(data)

    def fetch(self, data):
        self.temp_data.append({
            self._key.replace("?", ""): data
        })

    def commit(self, commit_no):
        self.data.append({
            commit_no: self.temp_data
        })
        self.temp_data = []

    def rollback(self):
        self.temp_data = []


class SimpleValueRule(Rule):
    def __init__(self, parent, val, key=""):
        super(SimpleValueRule, self).__init__(parent, key)
        self._val = val

    def match(self, data):
        assert self._val == data, "Value error {}, expect {}, but get {}".format(self._key, self._val, data)


class ValueTypeRule(Rule):
    def __init__(self, parent, type_, key=""):
        super(ValueTypeRule, self).__init__(parent, key=key)
        self._type = type_

    def match(self, data):
        assert isinstance(data, self._type), "Type error, expect type: {}, but get {}".format(self._type, type(data))


class KeyRule(Rule):
    def __init__(self):
        super(KeyRule, self).__init__(None)

    def match(self, data):
        assert self._key


class RuleWithChild(Rule):
    def __init__(self, parent, key=""):
        super(RuleWithChild, self).__init__(parent, key=key)
        self._children = []  # type: typing.List[Rule]

    def add_child(self, child: Rule):
        self._children.append(child)

    def match(self, data):
        raise NotImplementedError


class ListRule(RuleWithChild):
    def __init__(self, parent, templates, key=""):
        super(ListRule, self).__init__(parent, key=key)
        for item in templates:
            child_rule = rf.gen_rule(self, "", item)
            self.add_child(child_rule)

    def match(self, data):
        """
        默认每条规则至少有一项元素能匹配则通过
        :param data:
        :return:
        """
        assert isinstance(data, list)
        if self._children:
            assert data, "no data to match rules {}".format(self._key)
        for rule in self._children:
            matched = False
            msgs = []
            match_all = isinstance(rule, ListPatternAll)

            for item in data:
                try:
                    rule.try_match(item)
                    matched = True
                    if not match_all:
                        break
                except AssertionError as ex:
                    msgs.append(ex.args[0])
                    if match_all:
                        matched = False
                        break
                    # TODO

            if not matched:
                assert False, "None of element in list match the rule, detail: \n{}".format("\n".join(msgs))


class DictRule(RuleWithChild):
    def __init__(self, parent, template: dict, key=""):
        super(DictRule, self).__init__(parent, key=key)
        for k, v in template.items():
            child_rule = rf.gen_rule(self, k, v)
            self.add_child(child_rule)

    def match(self, data):
        assert isinstance(data, dict), "Type error, expect type: dict, but get {}".format(type(data))
        self.match_child(data)

    def match_child(self, data):
        for rule in self._children:
            optional = rule._key.startswith("?")
            key = rule._key.replace("?", "")
            key_exist = key in data.keys()
            if (not key_exist) and optional:
                continue

            assert key_exist, "Not match, except key: '{}' but not exist".format(rule._key)
            val = data.get(key.replace("?", ""))
            rule.try_match(val)


@labels
class LogicOpType(IntEnum):
    AND = 1
    OR = 2

    __labels__ = {
        AND: "logic_op_and",
        OR: "logic_op_or",
    }


class LogicOpRule(RuleWithChild):
    def __init__(self, parent, op: LogicOpType, templates, key=""):
        super(LogicOpRule, self).__init__(parent, key=key)
        self._op = op
        self._templates = templates
        for sub_tpl in templates:
            k = LogicOpType.label(op)
            sub_rule = rf.gen_rule(self, k, sub_tpl)
            self.add_child(sub_rule)

    @property
    def op(self):
        return self._op

    @property
    def templates(self):
        return self._templates

    def match(self, data):
        raise NotImplementedError


class LogicOpOR(LogicOpRule):
    def __init__(self, *templates):
        super().__init__(None, LogicOpType.OR, templates)

    def match(self, data):
        msgs = []
        for rule in self._children:
            try:
                return rule.match(data)
            except AssertionError as ex:
                msgs.append(ex.args[0])

        assert False, "\n".join(msgs)


class LogicOpAND(LogicOpRule):
    def __init__(self, template):
        super().__init__(None, LogicOpType.AND, template)

    def match(self, data):
        for rule in self._children:
            rule.match(data)


@labels
class MatchPatternType(IntEnum):
    ALL_IN_LIST = 1
    ANY_IN_LIST = 2

    __labels__ = {
        ALL_IN_LIST: "pattern_all",
        ANY_IN_LIST: "pattern_any",
    }


class ListPattern(RuleWithChild):
    def __init__(self, pattern: MatchPatternType):
        super(ListPattern, self).__init__(None)
        self._pattern = pattern


class ListPatternAll(ListPattern):
    def __init__(self, *templates):
        super(ListPatternAll, self).__init__(MatchPatternType.ALL_IN_LIST)
        self._templates = templates
        for sub_tpl in templates:
            k = MatchPatternType.label(self._pattern)
            sub_rule = rf.gen_rule(self, k, sub_tpl)
            self.add_child(sub_rule)

    def match(self, data):
        for rule in self._children:
            rule.try_match(data)


and_ = LogicOpAND
or_ = LogicOpOR
get_ = ValueFetcher
any_ = KeyRule()  # only check key exist, not check value
all_ = ListPatternAll


class RuleFactory:
    def gen_rule(self, parent, key, template):
        if isinstance(template, dict):
            rule = DictRule(parent, template, key=key)
        elif isinstance(template, list):
            rule = ListRule(parent, template, key=key)
        elif isinstance(template, (int, float, str, bool)):
            rule = SimpleValueRule(parent, template, key=key)
        elif template in (int, float, str, list, dict, bool):
            rule = ValueTypeRule(parent, template)
        elif isinstance(template, (LogicOpRule, ValueFetcher, KeyRule, ListPatternAll)):
            rule = template
            rule._key = key
            rule.parent = parent
            if isinstance(template, ValueFetcher):
                tx_map.update(rule.tx_key, rule.depth)
        else:
            raise NotImplementedError("type of {} not support yet".format(type(template)))

        return rule


rf = RuleFactory()

if __name__ == "__main__":
    pass

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

    # tpl = {
    #     "a": 1
    # }
    # rules = gen_rule(tpl)
    # rules.match({
    #     "a": 1
    # })

    # # ==============
    # tpl = {
    #     "a": {
    #         "b": 1
    #     }
    # }
    # rules = gen_rule(tpl)
    # rules.match({
    #     "a": {
    #         "b": 1
    #     }
    # })
    #
    # # ==============
    # tpl = {
    #     "a": {
    #         "b": {
    #             "c": 1
    #         }
    #     }
    # }
    # rules = gen_rule(tpl)
    # rules.match({
    #     "a": {
    #         "cc": "",
    #         "b": {
    #             "aa": 1,
    #             "c": 1
    #         }
    #     }
    # })
