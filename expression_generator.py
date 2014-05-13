#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import random

OPERATORS = ('+', '-', '*', '/')
BOOL_OPERATORS = ('<', '>')
EASY = 1
MEDIUM = 2
HARD = 3


class BinaryExpression():

    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def get_result(self):
        #     collision = False, False
        return eval('%s' % self)

    def get_expression_str(self, result):
        return '%s=%s' % (self, result)

    def get_true_expression(self):
        return self.get_expression_str(self.get_result())

    def get_false_expression(self):
        digits = len(str(self.get_result()))
        result = random.randint(10 * (digits - 1), 10 ** digits)
        # A little chance exists that true answer will be generated.
        while result == self.get_result():
            result = random.randint(10 * (digits - 1), 10 ** digits)
        return self.get_expression_str(result)

    def __str__(self):
        return '%d%s%d' % (self.left, self.op, self.right)


class BoolExpression():
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def get_expression(self, bool_value):
        for op in BOOL_OPERATORS:
            expr = '%s %s %s' % (self.left, op, self.right)
            if eval(expr) is bool_value:
                return expr
        raise 'It cant be'


def get_easy_expression():
    expression_type = random.random()
    if expression_type <= 0.75:
        left = random.randint(0, 10)
        right = random.randint(0, 10)
        op = random.choice(OPERATORS[:3])
    else:
        right = 2
        left = right * random.randint(0, 51)
        op = OPERATORS[3]

    return left, op, right


def get_medium_expression():
    expression_type = random.random()
    if expression_type <= 0.5:
        left = random.randint(-100, 100)
        right = random.randint(0, 100)
        op = random.choice(OPERATORS[:2])
    elif expression_type <= 0.75:
        left = random.randint(-10, 10)
        right = random.randint(0, 15)
        op = OPERATORS[2]
    else:
        right = random.randint(1, 10)
        left = right * random.randint(0, 100)
        op = OPERATORS[3]
    return left, op, right


def get_hard_expression():
    expression_type = random.random()
    if expression_type <= 0.5:
        left = random.randint(-1000, 1000)
        right = random.randint(0, 1000)
        op = random.choice(OPERATORS[:2])
    elif expression_type <= 0.75:
        left = random.randint(0, 100)
        right = random.randint(0, 100)
        op = OPERATORS[2]
    else:
        right = random.randint(1, 100)
        left = right * random.randint(0, 100)
        op = OPERATORS[3]
    return left, op, right


def get_bool_expression(truth, difficulty):
    if difficulty is EASY:
        left = random.randint(-100, 100)
        right = random.randint(-100, 100)
    elif difficulty is MEDIUM or difficulty is HARD:
        parts = get_medium_expression()
        left = ''.join([str(p) for p in parts])
        exp = BinaryExpression(*parts)
        answer = exp.get_result()
        if truth:
            right = random.randint(answer - 100, answer + 100)
        else:
            right = random.randint(-1000, 1000)

    exp = BoolExpression(left, right)
    return exp.get_expression(truth)


def get_expression(truth, difficulty):
    if difficulty is EASY:
        left, op, right = get_easy_expression()
    elif difficulty is MEDIUM:
        left, op, right = get_medium_expression()
    else:
        left, op, right = get_hard_expression()

    exp = BinaryExpression(left, op, right)
    if truth:
        return exp.get_true_expression()
    else:
        return exp.get_false_expression()


if __name__ == '__main__':
    print get_expression(True, EASY)
    print get_expression(False, EASY)
    print get_expression(True, MEDIUM)
    print get_expression(False, MEDIUM)
    print get_expression(True, HARD)
    print get_expression(False, HARD)

    print get_bool_expression(True, EASY)
    print get_bool_expression(False, EASY)
    print get_bool_expression(True, MEDIUM)
    print get_bool_expression(False, MEDIUM)
    print get_bool_expression(True, HARD)
    print get_bool_expression(False, HARD)
