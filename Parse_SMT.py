from Formula import *

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
    for char in smt:
        if char == '[':
            if cur:
                push(cur, groups, depth)
                cur = ""
            push([], groups, depth)
            depth += 1
        elif char == ']':
            if depth == 0:
                raise ValueError('Parentheses mismatch')
            if cur:
                push(cur, groups, depth)
                cur = ""
            depth -= 1
        else:
            cur += char
    if depth > 0:
        raise ValueError('Parentheses mismatch')
    return groups


def make_var(cur, neg, t_parser):
    data, name = t_parser(cur)
    f = Formula(FT.VAR, varName=name, data=data)
    if neg:
        f = Formula(FT.NEG, [f])
    return f


def string_helper(s: str, t_parser):
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
                    f = make_var(cur, neg, t_parser)
                    subformulas.append(f)
                    neg = False
                    cur = ""
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
    cur += flag
    if cur:
        f = make_var(cur, neg, t_parser)
        subformulas.append(f)
        neg = False
    return type, subformulas, neg


def parse_to_formula(l: list, t_parser):
    subformulas = []
    type = None
    neg = False
    for item in l:
        if isinstance(item, list):
            f = parse_to_formula(item, t_parser)
            if neg:
                f = Formula(FT.NEG, [f])
                neg = False
            subformulas.append(f)
        elif isinstance(item, str):
            t, s, neg = string_helper(item, t_parser)
            if not t:
                raise ValueError('Formula format mismatch')
            if not type:
                type = t
            elif type != t:
                raise ValueError('Formula type mismatch')
            subformulas.extend(s)
    if not type:
        raise ValueError('Formula format mismatch')
    return Formula(type, subformulas)


def parse(smt: str, t_parser):
    return parse_to_formula(parse_parentheses(smt), t_parser)


def foo(s):
    return s, s


s = "[a||[b==[c>>d]]]&&![[d>>c]>[!a&&b]]"
# lst = parse_parentheses(a)
# print(len(lst))
# print(lst)
a = Formula(FT.VAR, varName="a", data="a")
b = Formula(FT.VAR, varName="b", data="b")
c = Formula(FT.VAR, varName="c", data="c")
d = Formula(FT.VAR, varName="d", data="d")

formula = (a | (Formula(FT.IFF, [b, d <= c]))) & -((-a & b) <= (c <= d))
print(parse(s, foo) == formula)
