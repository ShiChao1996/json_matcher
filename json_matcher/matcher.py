# coding:utf-8
"""
@time: 2021/1/9 3:30 下午
@author: shichao
"""
import json

from json_matcher.rule import rf


class JsonMatcher(object):
    def __init__(self, tpl):
        self.tpl = tpl
        self.rule = rf.gen_rule(None, "", tpl)
        self.is_last_match = False

    def is_match(self, data):
        """
        check if data matches the struct of template, returns match result and reason
        :param data:
        :return:
        """
        try:
            self.rule.match(data)
            self.is_last_match = True
            return True, ""
        except AssertionError as ex:
            return False, ex.args[0]

    def find_from_json(self, d):
        self.is_last_match = False
        matched_data = self._find_from(d)
        if matched_data:
            self.is_last_match = True
            return matched_data

        return None

    def find_from_json_str(self, s):
        try:
            json_data = json.loads(s)
        except Exception:
            raise Exception("Not valid json str !")
        return self.find_from_json(json_data)

    def _find_from(self, d):
        if not isinstance(d, (list, dict)):
            return None

        if isinstance(d, list):
            for item in d:
                data = self._find_from(item)
                if data:
                    return data

            return None

        match, _ = self.is_match(d)
        if match:
            return d

        for v in d.values():
            match_data = self._find_from(v)
            if match_data:
                return match_data

        return None

    def get_data(self):
        if self.is_last_match:
            return self.rule.combine_data()
        return "not matched"


if __name__ == "__main__":
    tpl = {
        "a": 1,
        "b": {
            "bb": 2
        }
    }
    matcher = JsonMatcher(tpl)

    data1 = {
        "a": 1,
        "b": {
            "bb": 2
        },
        "c": 123
    }
    ok, msg = matcher.is_match(data1)
    print(ok, msg)
    # True, ""

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
