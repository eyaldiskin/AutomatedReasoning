from Formula import *
from TUF import TUF

logic = {"~": FT.NEG, "&&": FT.AND, "||": FT.OR, ">>": FT.IMPLIES, "==": FT.IFF}
spacial_chars = "|&>="


def push(obj, lst, depth):
    while depth:
        lst = lst[-1]
        depth -= 1
    lst.append(obj)


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
    if cur:
        groups.append(cur)
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
                    subformulas.append(make_var(cur, neg, t_parser))
                    neg = False
                    cur = ""
            elif flag == '':
                flag = char
            else:
                cur += flag + char
                flag = ''
        elif char == '~' and not cur and not flag:
            neg = True
        else:
            cur += flag + char
            flag = ''
    cur += flag
    if cur:
        subformulas.append(make_var(cur, neg, t_parser))
        neg = False
        if not type:
            type = FT.VAR
    return type, subformulas, neg


def parse_to_formula(lst: list, t_parser):
    subformulas = []
    type = None
    neg = False
    neg_all = False
    for item in lst:
        if isinstance(item, list):
            f = parse_to_formula(item, t_parser)
            if neg:
                f = Formula(FT.NEG, [f])
                neg = False
            subformulas.append(f)
        elif isinstance(item, str):
            if item == '~' and not subformulas:
                neg = neg_all = True
                continue
            temp_type, formula, neg = string_helper(item, t_parser)
            # if neg and not subformulas:
            #     temp_type = FT.NEG
            if not temp_type:
                raise ValueError('Formula format mismatch')
            if not type:
                type = temp_type
            elif type != temp_type:
                raise ValueError('Formula type mismatch')
            subformulas.extend(formula)
    if type == FT.VAR or (neg_all and not type):
        return subformulas[0]
    if not type:
        raise ValueError('Formula format mismatch')
    return Formula(type, subformulas)


def parse(smt: str, t_parser):
    return parse_to_formula(parse_parentheses(smt), t_parser)


def foo(s):
    return s, s


if __name__ == "__main__":
    s = "~[[a||[b==[c>>d]]]&&~[[d>>c]>>[~a&&b]]]"
    a = Formula(FT.VAR, varName="a", data="a")
    b = Formula(FT.VAR, varName="b", data="b")
    c = Formula(FT.VAR, varName="c", data="c")
    d = Formula(FT.VAR, varName="d", data="d")

    # formula = -((a | (Formula(FT.IFF, [b, d <= c]))) & -((-a & b) <= (c <= d)))
    # print(parse(s, foo) == formula)

    # s = "a=b"
    # print(parse(s, foo) == Formula(FT.VAR))

    x = Formula(FT.VAR, varName="f(f(x,y),z)=f(x,y)", data="d")
    y = Formula(FT.VAR, varName="f(x,y)=f(f(x,y),z)", data="d")

    t = TUF()
    # d = t.parse("f(f(x,y),z)=f(x,y)")
    s = "f(f(x,y),z)=f(x,y)&&f(x,y)=f(f(x,y),z)"
    print(parse(s, t.parse) == x & x)
