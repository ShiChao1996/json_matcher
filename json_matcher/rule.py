# coding:utf-8
"""
@time: 2021/1/10 3:24 下午
@author: shichao
"""
import typing
from enum import IntEnum

from json_matcher.util import labels


class Rule:
    def __init__(self, key=""):
        self._key = key

    def match(self, data):
        raise NotImplementedError

    def get_data(self):
        data = []
        if isinstance(self, ValueFetcher):
            data.extend(self.data)

        if isinstance(self, RuleWithChild):
            for sub_rule in self._children:
                sub_data = sub_rule.get_data()
                data.extend(sub_data)

        return data


class ValueFetcher(Rule):
    def __init__(self, with_key=True):
        self.with_key = with_key
        self.data = []
        super(ValueFetcher, self).__init__()

    def match(self, data):
        self.fetch(data)

    def fetch(self, data):
        self.data.append({
            self._key: data
        })


get_ = ValueFetcher


class RuleWithChild(Rule):
    def __init__(self, key=""):
        super(RuleWithChild, self).__init__(key=key)
        self._children = []  # type: typing.List[Rule]

    def add_child(self, child: Rule):
        self._children.append(child)

    def match(self, data):
        raise NotImplementedError


class ListRule(RuleWithChild):
    def __init__(self, templates, key=""):
        super(ListRule, self).__init__(key)
        for item in templates:
            child_rule = rf.gen_rule("", item)
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
            for item in data:
                try:
                    rule.match(item)
                    matched = True
                    break
                except AssertionError as ex:
                    msgs.append(ex.args[0])
            if not matched:
                assert False, "None of element in list match the rule, detail: \n{}".format("\n".join(msgs))


class DictRule(RuleWithChild):
    def __init__(self, template: dict, key=""):
        super(DictRule, self).__init__(key=key)
        for k, v in template.items():
            child_rule = rf.gen_rule(k, v)
            self.add_child(child_rule)

    def match(self, data):
        assert isinstance(data, dict), "Type error, expect type: dict, but get {}".format(type(data))
        self.match_child(data)

    def match_child(self, data):
        for rule in self._children:
            if rule._key:
                assert rule._key in data.keys(), "Not match, except key: '{}' but not exist".format(rule._key)
            val = data.get(rule._key)
            rule.match(val)


class SimpleValueRule(Rule):
    def __init__(self, val, key=""):
        super(SimpleValueRule, self).__init__(key)
        self._val = val

    def match(self, data):
        assert self._val == data, "Value error {}, expect {}, but get {}".format(self._key, self._val, data)


class ValueTypeRule(Rule):
    def __init__(self, type_, key=""):
        super(ValueTypeRule, self).__init__(key)
        self._type = type_

    def match(self, data):
        assert isinstance(data, self._type), "Type error, expect type: {}, but get {}".format(self._type, type(data))


class KeyRule(Rule):
    def __init__(self):
        super(KeyRule, self).__init__()

    def match(self, data):
        assert self._key


@labels
class LogicOpType(IntEnum):
    AND = 1
    OR = 2

    __labels__ = {
        AND: "logic_op_and",
        OR: "logic_op_or",
    }


class LogicOpRule(RuleWithChild):
    def __init__(self, op: LogicOpType, templates, key=""):
        super(LogicOpRule, self).__init__(key=key)
        self._op = op
        self._templates = templates
        for sub_tpl in templates:
            k = LogicOpType.label(op)
            sub_rule = rf.gen_rule(k, sub_tpl)
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
        super().__init__(LogicOpType.OR, templates)

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
        super().__init__(LogicOpType.AND, template)

    def match(self, data):
        for rule in self._children:
            rule.match(data)


and_ = LogicOpAND
or_ = LogicOpOR
any_ = KeyRule()  # only check key exist, not check value


class RuleFactory:
    def gen_rule(self, key, template):
        if isinstance(template, dict):
            rule = DictRule(template, key=key)
        elif isinstance(template, list):
            rule = ListRule(template, key=key)
        elif isinstance(template, (int, float, str, bool)):
            rule = SimpleValueRule(template, key=key)
        elif template in (int, float, str, list, dict, bool):
            rule = ValueTypeRule(template)
        elif isinstance(template, (LogicOpRule, ValueFetcher, KeyRule)):
            rule = template
            rule._key = key
        else:
            raise NotImplementedError("type of {} not support yet".format(type(template)))

        return rule


rf = RuleFactory()

if __name__ == "__main__":
    pass
    # tpl = {
    #     "a": [
    #         {
    #             "aa": 1,
    #             "bb": any_
    #         }
    #     ]
    # }
    # rule = rf.gen_rule("", tpl)
    # rule.match({
    #     "a": [
    #         {
    #             "aa": 1,
    #             "bbb": [1, 2, 3]
    #         },
    #     ]
    # })
    # data = rule.get_data()
    # print(data)
    #
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
