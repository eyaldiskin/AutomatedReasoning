from UFData import *
from UnionFind import UnionFind


class TUF:
    def __init__(self):
        self.vars = dict()
        self.functions = dict()
        self.union_find = UnionFind()
        self.equations = []

    # def _get_symbols(self, formula: Formula):
    #     if formula.type == Formula.FT.VAR:
    #         if getattr(formula, "data", None):
    #             self._insert_symbol(formula.data)
    #         return
    #     for clause in formula.formulas:
    #         if clause.type == Formula.FT.VAR:
    #             if getattr(clause, "data", None):
    #                 self._insert_symbol(clause.data)
    #         else:
    #             self._get_symbols(clause)
    #
    # def _insert_symbol(self, data: TData):
    #     name = data.name
    #     type = data.type
    #     for t in TType:
    #         if t != type and name in self.symbols[t]:
    #             raise
    #     if type == TType.VAR:
    #         self.symbols[type][name] = name
    #         return
    #     arity = len(data.arguments)
    #     if name in self.symbols[type] and self.symbols[type][name] != arity:
    #         raise
    #     else:
    #         self.symbols[type][name] = arity
    #     for argument in data.arguments:
    #         self._insert_symbol(argument)

    def conflict(self, eq_list, dif_list):
        self.union_find.reset()
        for equation in eq_list:
            args = equation.arguments
            self.union_find.add_equation(args[0], args[1])
        for inequality in dif_list:
            args = inequality.arguments
            if self.union_find.are_equal(args[0], args[1]):
                conflict = [[inequality, True]]
                for equation in eq_list:
                    if self.union_find.are_equal(equation.arguments[0], args[0]):
                        conflict.append([equation, False])
                return conflict
        return None

    def propagate(self):
        pass

    def learn(self):
        pass

    # from here we deal with parsing

    def parse(self, formula: str):
        sides = formula.split("=")
        if len(sides) != 2:
            raise ValueError('Formula format mismatch')
        left = self._parse_helper(sides[0])[0]
        right = self._parse_helper(sides[1])[0]
        self.union_find.insert_element(left)
        self.union_find.insert_element(right)

        # this part deals with the symmetry of equality
        data = UFData(UFType.PRED, '=', [right, left])
        if data in self.equations:
            return data, "=".join(reversed(sides))
        data = UFData(UFType.PRED, '=', [left, right])
        self.equations.append(data)
        return data, formula

    def _parse_helper(self, formula: str):
        subformulas = []
        args = ""
        depth = 0
        name = ""
        for char in formula:
            if depth:
                if char == ')':
                    depth -= 1
                    if depth:
                        args += char
                    else:
                        subformulas.append(self._add_func(name, args))
                        args = ""
                        name = ""
                else:
                    args += char
                    if char == '(':
                        depth += 1
            else:
                if char == ')':
                    raise ValueError('Parentheses mismatch')
                if char == '(':
                    depth += 1
                elif char == ',':
                    if name:
                        subformulas.append(self._add_var(name))
                        name = ""
                else:
                    name += char
        if depth:
            raise ValueError('Parentheses mismatch')
        if name:
            subformulas.append(self._add_var(name))
        return subformulas

    def _add_var(self, name):
        if name in self.functions:
            raise
        if name not in self.vars:
            self.vars[name] = UFData(UFType.VAR, name)
        return self.vars[name]

    def _add_func(self, name, args):
        if name in self.vars:
            raise
        arg_list = self._parse_helper(args)
        if name in self.functions and self.functions[name] != len(arg_list):
            raise
        self.functions[name] = len(arg_list)
        return UFData(UFType.FOO, name, arg_list)


# t = TUF()
# d = t.parse("f(f(x,y),z)=f(x,y)")
# print("hi")
