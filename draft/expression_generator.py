#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import random

OPERATORS = ('+', '-', '*', '/')
EASY = 1
MEDIUM = 2
HARD = 3


class BinaryExpression():

    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __get_result(self):
        return eval('%s' % self)

    def get_expression_str(self, result):
        return '%s=%s' % (self, result)

    def get_true_expression(self):
        return self.get_expression_str(self.__get_result())

    def get_false_expression(self):
        digits = len(str(self.__get_result()))
        result = random.randint(10 * (digits - 1), 10 ** digits)
        # A little chance exists that true answer will be generated.
        while result == self.__get_result():
            result = random.randint(10 * (digits - 1), 10 ** digits)
        return self.get_expression_str(result)

    def __str__(self):
        return '%d%s%d' % (self.left, self.op, self.right)


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
    pass
    # print OPERATORS[:2]
    # a = BinaryExpression(1, '/', 2)
    # print a.get_true_expression()
    # print '\u00f7'.encode('utf8').decode('utf8')
