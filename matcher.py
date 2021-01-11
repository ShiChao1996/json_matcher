# coding:utf-8
"""
@time: 2021/1/9 3:30 下午
@author: shichao
"""

from json_matcher.rule import gen_rule


class JsonMatcher(object):
    def __init__(self, tpl):
        self.tpl = tpl
        self.rule = gen_rule(tpl)
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

    def find_target_dict(self, d):
        if not isinstance(d, (list, dict)):
            return None

        if isinstance(d, list):
            for item in d:
                data = self.find_target_dict(item)
                if data:
                    return data

            return None

        match, _ = self.is_match(d)
        if match:
            return d

        for v in d.values():
            match_data = self.find_target_dict(v)
            if match_data:
                return match_data

        return None

    def get_data(self):
        if self.is_last_match:
            return self.rule.get_data()
        return "not matched"
