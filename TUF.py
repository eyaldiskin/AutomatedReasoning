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

    def _set_eq(self, eq_list):
        self.union_find.reset()
        for equation in eq_list:
            args = equation.arguments
            self.union_find.add_equation(args[0], args[1])

    def conflict(self, eq_list, dif_list):
        self._set_eq(eq_list)
        for inequality in dif_list:
            args = inequality.arguments
            if self.union_find.are_equal(args[0], args[1]):
                conflict = [[equation, False] for equation in eq_list]
                conflict.append([inequality, True])
                return conflict
        return None

    def _find_implication(self, equation, eq_list):
        """
        find a local minimum of equations in eq_list that imply equation.
        if eq_list doesn't imply equation, return None.
        """
        if not eq_list or not equation:
            return None
        self._set_eq(eq_list)
        args = equation.arguments
        if not self.union_find.are_equal(args[0], args[1]):
            return None
        eq_lst_cpy = list(eq_list)
        for eq in eq_list:
            eq_lst_cpy.remove(eq)
            self._set_eq(eq_lst_cpy)
            if not self.union_find.are_equal(args[0], args[1]):
                eq_lst_cpy.append(eq)
        return eq_lst_cpy

    def _explain_true(self, data, level, eq_list, eq_levels, dif_list, dif_levels):
        low_level_eq = [x for x in eq_list if eq_levels[eq_list.index(x)] < level]
        low_level_dif = [x for x in dif_list if dif_levels[dif_list.index(x)] < level]
        low_level_dif.append(data)
        for equation in low_level_eq:
            implication_list = self._find_implication(equation, low_level_dif)
            if implication_list and data in implication_list:
                new_conflict = [[x, True] for x in implication_list if not x == data]
                new_conflict.append([equation, False])
                return new_conflict
        return None

    def _explain_false(self, data, level, dif_list, dif_levels):
        low_level = [x for x in dif_list if dif_levels[dif_list.index(x)] < level]
        implication_list = self._find_implication(data, low_level)
        if implication_list:
            return [[x, True] for x in implication_list]
        return None

    def explain(self, conflict, eq_list, dif_list, eq_levels, dif_levels):  # todo finish
        new_conflict = []
        temp_conflict = None
        remove_level = -1
        to_remove = None
        for constrain in conflict:
            data, assignment = constrain
            if assignment:
                level = dif_levels[dif_list.index(data)]
                if level > remove_level:
                    temp_conflict = self._explain_true(data, level, eq_list, eq_levels, dif_list, dif_levels)
            else:
                level = eq_levels[eq_list.index(data)]
                if level > remove_level:
                    temp_conflict = self._explain_false(data, level, dif_list, dif_levels)
            if temp_conflict:
                to_remove = constrain
                new_conflict = temp_conflict
        if to_remove:
            conflict.remove(to_remove)
            conflict.extend([var for var in new_conflict if var not in conflict])
        return conflict

    def propagate(self, eq_list, dif_list, unknown_list):
        self._set_eq(eq_list)
        deduced = []
        to_check = []
        for equation in unknown_list:
            args = equation.arguments
            if self.union_find.are_equal(args[0], args[1]):
                deduced.append([equation, True])
            else:
                to_check.append(equation)

        self.union_find.save()
        for equation in to_check:
            self.union_find.load()
            args = equation.arguments
            self.union_find.add_equation(args[0], args[1])
            for inequality in dif_list:
                args = inequality.arguments
                if self.union_find.are_equal(args[0], args[1]):
                    deduced.append([equation, False])
        return deduced

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
