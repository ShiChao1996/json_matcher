# coding:utf-8
"""
@time: 2021/1/9 3:30 下午
@author: shichao
"""

from enum import IntEnum

import attr



class RuleType(IntEnum):
    EXIST_KEY = 1
    MATCH_KEY_VALUE = 2
    VALUE_MATCH_TYPE = 3
    EXIST_LIST_VALUE = 4
    EXIST_DICT_VALUE = 5
    DIV_CHILDREN = 999


@attr.s(slots=True)
class Rule(object):
    rule_type = attr.ib(default=0)
    key = attr.ib(default="")
    val = attr.ib(default=None)
    children = attr.ib(factory=list)
    val_type = attr.ib(default=0)
    sub_checker = attr.ib(default=None)


class JsonChecker(object):
    def __init__(self, template):
        self._template = template
        self._rules = self._gen_rule(template)

    def _gen_rule(self, d, prefix=""):
        rules = []

        if isinstance(d, dict):
            items = d.items()
            for k, v in items:
                rule = Rule(key=k)
                if isinstance(v, dict):
                    rule.children = self._gen_rule(v)
                    rule.rule_type = RuleType.VALUE_MATCH_TYPE
                    rule.val_type = dict
                elif isinstance(v, list):
                    rule.children = self._gen_rule(v, prefix=rule.key)
                    rule.rule_type = RuleType.DIV_CHILDREN
                else:
                    if v == dict:
                        rule.rule_type = RuleType.VALUE_MATCH_TYPE
                        rule.val_type = dict
                    elif v == list:
                        rule.rule_type = RuleType.VALUE_MATCH_TYPE
                        rule.val_type = list
                    elif v == int:
                        rule.rule_type = RuleType.VALUE_MATCH_TYPE
                        rule.val_type = int
                    elif v == str:
                        rule.rule_type = RuleType.VALUE_MATCH_TYPE
                        rule.val_type = str
                    else:
                        rule.val = v
                        rule.rule_type = RuleType.MATCH_KEY_VALUE

                rules.append(rule)

        elif isinstance(d, list):
            for item in d:
                rule = Rule(key=prefix)
                if isinstance(item, dict):
                    rule.children = self._gen_rule(item)
                    rule.rule_type = RuleType.VALUE_MATCH_TYPE
                    rule.val_type = dict
                elif isinstance(item, list):
                    rule.children = self._gen_rule(item, prefix=rule.key)
                    rule.rule_type = RuleType.DIV_CHILDREN
                else:
                    rule.rule_type = RuleType.EXIST_LIST_VALUE
                    rule.val = item
                rules.append(rule)

        return rules

    def check_rule(self, data):
        try:
            self._check_rule(self._rules, data)
        except AssertionError as ex:
            return False, ex.args

        return True, ""

    def _check_rule(self, rules, data):
        if not rules:
            return True
        assert isinstance(data, (list, dict)), "invalid data type {}".format(data)

        if isinstance(data, dict):
            for rule in rules:
                val = data.get(rule.key)
                if rule.rule_type == RuleType.EXIST_KEY:
                    assert rule.key in data.keys(), "key: {} not exist".format(rule.key)
                if rule.rule_type == RuleType.MATCH_KEY_VALUE:
                    msg_fmt = "key {}'s value not match, expect:{}, but get:{}"
                    assert rule.val == val, msg_fmt.format(rule.key, rule.val, val)
                if rule.rule_type == RuleType.VALUE_MATCH_TYPE:
                    msg_fmt = "key {}'s value type not match, expect:{}, but get:{}"
                    assert isinstance(val, rule.val_type), msg_fmt.format((rule.key, rule.val_type, type(val)))

                if rule.children:
                    print("ready to check children")
                    ok = self._check_rule(rule.children, val)
                    if not ok:
                        return False
        else:
            for rule in rules:
                if rule.rule_type == RuleType.VALUE_MATCH_TYPE:
                    msg_fmt = "key {}'s value type not match, expect:{}, but get:{}"
                    for item in data:
                        assert isinstance(item, rule.val_type), msg_fmt.format(rule.key, rule.val_type, type(item))

                if rule.rule_type == RuleType.EXIST_LIST_VALUE:
                    print("assert list val")
                    assert isinstance(data, list) and rule.val in data, "list {} does't exist val {}".format(rule.key,
                                                                                                             rule.val)

                # 应该有两种模式，1：列表每一项都匹配，2：列表任意一项符合
                for item in data:
                    ok = self._check_rule(rule.children, item)
                    if ok:
                        break
                    # if not ok:
                    #     return False
        return True


class LogicOpType(IntEnum):
    AND = 1
    OR = 2


class LogicOp(JsonChecker):

    def __init__(self, op: LogicOpType, template: list):
        self._op = op
        super(LogicOp, self).__init__(template)

    def check(self, data):
        pass


class LogicOpOR(LogicOp):
    def __init__(self, template):
        super().__init__(LogicOpType.OR, template)

    def check(self, data):
        for rule in self._rules:
            ok = self._check_rule([rule], data)
            if ok:
                return True

        return False


class LogicOpAND(LogicOp):
    def __init__(self, template):
        super().__init__(LogicOpType.AND, template)

    def check(self, data):
        for rule in self._rules:
            ok = self._check_rule([rule], data)
            if not ok:
                return False

        return True


and_ = LogicOpAND
or_ = LogicOpOR
