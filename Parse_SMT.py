# import SMT
from Formula import *
# import re

logic = {"!": FT.NEG, "&&": FT.AND, "||": FT.OR, ">>": FT.IMPLIES, "==": FT.IFF}
spacial_chars = "|&>="


def push(obj, l, depth):
    while depth:
        l = l[-1]
        depth -= 1
    l.append(obj)


def parse_parentheses(smt: str):
    groups = []
    depth = 0
    cur = ""
    try:
        for char in smt:
            if char == '[':
                if cur:
                    push(cur, groups, depth)
                    cur = ""
                push([], groups, depth)
                depth += 1
            elif char == ']':
                if cur:
                    push(cur, groups, depth)
                    cur = ""
                depth -= 1
            else:
                # push(char, groups, depth)
                cur += char
    except IndexError:
        raise ValueError('Parentheses mismatch')

    if depth > 0:
        raise ValueError('Parentheses mismatch')
    else:
        return groups


def string_helper(s: str):
    subformulas = []
    cur = ""
    flag = ''
    type = None
    neg = False
    for char in s:
        if char in spacial_chars:
            if char == flag:
                flag = ''
                if not type:
                    type = logic[char * 2]
                elif type != logic[char * 2]:
                    raise ValueError('Formula type mismatch')
                if cur:
                    data, name = cur, cur # todo add theory parser
                    cur = ""
                    f = Formula(FT.VAR, varName=name, data=data)
                    if neg:
                        f = Formula(FT.NEG, [f])
                        neg = False
                    subformulas.append(f)
            elif flag == '':
                flag = char
            else:
                cur += flag + char
                flag = ''
        elif char == '!' and not cur and not flag:
            neg = True
        else:
            cur += flag + char
            flag = ''
    return type, subformulas, neg


def parse_to_formula(l: list):
    subformulas = []
    type = FT.VAR
    neg = False
    for item in l:
        if isinstance(item, list):
            f = parse_to_formula(item)
            if neg:
                f = Formula(FT.NEG, [f])
                neg = False
            subformulas.append(f)
        elif isinstance(item, str):
            type, s, neg = string_helper(item)
            subformulas.extend(s)
    return Formula(type, subformulas)


def parse(smt: str):
    l = parse_parentheses(smt)
    f = parse_to_formula(l)
    return f


a = "[a||[b==[c>>d]]]&&![[d>>c]>>[!a&&b]]"
# lst = parse_parentheses(a)
# print(len(lst))
# print(lst)
print(parse(a))