from CDCL import CDCL
import Formula
from TData import *
from UnionFind import UnionFind


class TUF:
    # def __init__(self, formula: Formula):
    def __init__(self):
        # self.cdcl = CDCL(formula)
        # self.congruence = [UnionFind(formula)]
        self.vars = dict()
        self.functions = dict()
        # self.symbols = dict()
        # for t in TType:
        #     self.symbols[t.name] = dict()
        # self._get_symbols(self.cdcl.formula)

    def _get_symbols(self, formula: Formula):
        if formula.type == Formula.FT.VAR:
            if getattr(formula, "data", None):
                self._insert_symbol(formula.data)
            return
        for clause in formula.formulas:
            if clause.type == Formula.FT.VAR:
                if getattr(clause, "data", None):
                    self._insert_symbol(clause.data)
            else:
                self._get_symbols(clause)

    def _insert_symbol(self, data: TData):
        name = data.name
        type = data.type
        for t in TType:
            if t != type and name in self.symbols[t]:
                raise
        if type == TType.VAR:
            self.symbols[type][name] = name
            return
        arity = len(data.arguments)
        if name in self.symbols[type] and self.symbols[type][name] != arity:
            raise
        else:
            self.symbols[type][name] = arity
        for argument in data.arguments:
            self._insert_symbol(argument)

    def congruence_closure(F, M):
        pass

    def _T_conflict(F, M):
        pass

    def _T_propagate(F, M):
        pass

    def T_learn(self):
        pass

    def solve(self):
        pass

    def parse(self, formula: str):
        rhs = False
        index = 0
        for i in range(len(formula)):
            if formula[i] == '=':
                if rhs:
                    raise ValueError('Formula format mismatch')
                rhs = True
                index = i

        left = self.parse_helper(formula[0:index])[0]
        right = self.parse_helper(formula[index+1:len(formula)])[0]
        return TData(TType.PRED, '=', [left, right])

    def parse_helper(self, formula: str):
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
            self.vars[name] = TData(TType.VAR, name)
        return self.vars[name]

    def _add_func(self, name, args):
        if name in self.vars:
            raise
        arg_list = self.parse_helper(args)
        if name in self.functions and self.functions[name] != len(arg_list):
            raise
        self.functions[name] = len(arg_list)
        return TData(TType.FOO, name, arg_list)


t = TUF()
data = t.parse("f(f(x,y),z)=f(x,y)")
print("hi")