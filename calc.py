# -*- coding: utf-8 -*-

import types
import math
from fractions import Fraction


# 四則演算子
def add(a, b): return a + b
def sub(a, b): return a - b
def mul(a, b): return a * b
# 通常の割り算だと切り捨てるため，Fractionを使う
def div(a, b): return Fraction(a, b)


OPERATORS = {add: '+', sub: '-', mul: '*', div: '/'}
# OPERATORS の逆の対応付け
OPR2FUNCS = dict((v, k) for k, v in OPERATORS.iteritems())


# ---------------------------------------------------------------------------
# 逆ポーランド記法の計算

def calcList(L):
    """ 逆ポーランド記法を表すリストから計算をした結果を返す

    L : 数値と演算子の関数のリスト。
        ex. [3, 8, 2, add, mul, 4, add, 5, sub]
    """
    S = []
    try:
        for e in L:
            if isinstance(e, types.FunctionType):
                # 関数の場合はスタックの末尾から二つ要素を取り出し、
                # 関数を適用。結果をスタックに追加
                S.append(e(S.pop(-2), S.pop(-1)))
            else:
                S.append(e)

        # 最終的にスタックに値が一つでなければ不適切な式だったとしてエラーとする
        if not len(S) == 1: raise InvalidExpressionError
        return S[0]
    except:
        raise InvalidExpressionError


class InvalidExpressionError(Exception):
    pass


# ---------------------------------------------------------------------------
# 逆ポーランド記法を中置記法へ変換

def cnvExpList(L):
    """ 逆ポーランド記法を表わしたリストを、二項演算ごとにネストしたリストに変換

    ex. [3, 8, 2, add, mul, 4, add, 5, sub]
        → [[[3, [8, 2, add], mul], 4, add], 5, sub]
    """
    i = 0
    while i < (len(L) - 2):
        if type(L[i]) in [int, float, list] and \
                        type(L[i + 1]) in [int, float, list] and \
                        type(L[i + 2]) is types.FunctionType:
            L.insert(i, [L.pop(i), L.pop(i), L.pop(i)])
            if len(L) == 1:
                break
            else:
                i = 0; continue
        i += 1

    # 式が妥当であればリストの要素は 1 になる。
    if not len(L) == 1 or not isinstance(L[0], list):
        raise InvalidExpressionError
    # 一番外側の括弧をはずす
    return reduce(lambda a, b: a + b, L, [])


def cnvExp(L):
    """ 二項演算ごとにネストしたリストを式の文字列に変換

    ex. [[[3, [8, 2, add], mul], 4, add], 5, sub]
        → (((3*(8+2))+4)-5)
    """
    if isinstance(L, list):
        return '(' + cnvExp(L[0]) + OPERATORS[L[2]] + cnvExp(L[1]) + ')'
    else:
        return str(L)


def delOuterBrackets(L):
    """ 式の一番外側の括弧を削除

    ex. (((3*(8+2))+4)-5) → ((3*(8+2))+4)-5
    """
    import re
    return re.sub(r'^\((.+)\)$', r'\1', L)


# ---------------------------------------------------------------------------
# 逆ポーランド記法の文字列をリストへ変換

def conv2List(rpn):
    """ 逆ポーランド記法で書かれた文字列をリストに変換

    ただし、整数にできるものは整数に変換。演算子は関数に変換。
    ex. "3 8 2 + * 4 + 5 -"
        → [3, 8, 2, add, mul, 4, add, 5, sub]
    """
    return [(int(math.modf(float(x))[1])
             if math.modf(float(x))[0] == 0 else float(x))
            if x not in ['+', '-', '*', '/'] else OPR2FUNCS[x]
            for x in rpn.split()]


def infixNotation(rpn):
    """ 中置記法に変換 """
    # リストをコピー
    cloneL = reduce(lambda a, b: a + [b], conv2List(rpn), [])
    return delOuterBrackets(cnvExp(cnvExpList(cloneL)))


def calc(s):
    """ 計算した結果を返す """
    return calcList(conv2List(s))


def infixToPostfix(infixexer):
    input = infixexer.split(" ")
    buff = []
    stack = []

    while len(input):
        token = input.pop(0)
        # print stack
        if token.isalnum():
            buff.append(token)
        else:
            if not len(stack):
                stack.append(token)
            else:
                if checkPriority(token, stack[-1]):
                    while len(stack) and checkPriority(token, stack[-1]):
                            buff.append(stack.pop())
                    stack.append(token)
                else:
                    stack.append(token)
    else:
        while len(stack):
            buff.append(stack.pop())

    return " ".join(buff)


def checkPriority(token, stack):

    if token == "+":
        if stack in "+/*-":
            return 1
    elif token == "-":
        if stack in "-/*":
            return 1
    elif token == "*":
        if stack in "*/":
            return 1
    else:
        if stack in "/":
            return 1
    return 0


def less_or_equal_prec(a,b):
    #aの優先順位がbの優先順位より低いか等しいとき真となる
    if a in ('*','/') and b in ('*','/'):
        return True
    elif a in ('+','-') and b in ('+','-','*','/'):
        return True
    else: return False


if __name__ == "__main__":
    # test = "6 - 2 - 2"
    # # 62-2-
    # test = "7 - 2 + 9"
    # test = "10 * 9 / 7"
    # result = infixToPostfix(test)
    print "Infix:   "+test
    print "Postfix: "+(infixToPostfix(test))
    print infixNotation(result), '=', calc(result)
