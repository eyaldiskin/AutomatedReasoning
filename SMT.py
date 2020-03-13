from CDCL import CDCL
import Formula
import Parse_SMT


class SMT:
    def __init__(self, smt: str, theory):
        self.theory = theory
        self.cdcl = CDCL(Parse_SMT.parse(smt, theory.parse))
        self.M = []

    def _get_assigned_vars(self):
        assignment = self.cdcl.partialAssignment
        var_true = []
        var_false = []
        for var in assignment:
            data = self.cdcl.formula.varFinder[var].data
            if data:
                if assignment[var]:
                    var_true.append(data)
                else:
                    var_false.append(data)
        return var_true, var_false

    def _get_part_assignment(self):
        formula = self.cdcl.formula
        assignment = self.cdcl.partialAssignment
        var_true, var_false = self._get_assigned_vars()
        var_unknown = []
        for var_name in formula.variables:
            data = formula.varFinder[var_name].data
            if data and var_name not in assignment:
                var_unknown.append(data)
        return var_true, var_false, var_unknown

    def _get_var_name_by_data(self, data):
        formula = self.cdcl.formula
        for var_name in formula.variables:
            var_data = formula.varFinder[var_name].data
            if var_data and data == var_data:
                return var_name
        return None

    def _conflict(self):
        var_true, var_false = self._get_assigned_vars()
        if var_true or var_false:
            return self.theory.conflict(var_true, var_false)
        return None

    def _propagate(self):
        while True:
            var_true, var_false, var_unknown = self._get_part_assignment()
            new_vars = self.theory.propagate(var_true, var_false, var_unknown)
            if not new_vars:
                break
            for data, assignment in new_vars:
                # data, assignment = assigned_var
                var_name = self._get_var_name_by_data(data)
                var = self.cdcl.formula.varFinder[var_name]
                self.cdcl.assign(var, assignment)

    def _explain(self, conflict):
        var_true, var_false = self._get_assigned_vars()
        names_true = [self._get_var_name_by_data(data) for data in var_true]
        names_false = [self._get_var_name_by_data(data) for data in var_false]
        nodes = self.cdcl.graph.nodes
        true_lvls = [-1] * len(var_true)
        false_lvls = [-1] * len(var_false)
        for node in nodes:
            if node.varName in names_true:
                true_lvls[names_true.index(node.varName)] = node.level
            elif node.varName in names_false:
                false_lvls[names_false.index(node.varName)] = node.level

        new_conflict = self.theory.explain(conflict, var_true, var_false, true_lvls, false_lvls)
        while new_conflict != conflict:
            conflict = new_conflict
            new_conflict = self.theory.explain(conflict, var_true, var_false, true_lvls, false_lvls)
        return new_conflict

    def _conflict_to_formula(self, conflict):
        literals = []
        for data, assignment in conflict:
            var_name = self._get_var_name_by_data(data)
            var = self.cdcl.formula.varFinder[var_name]
            if not assignment:
                var = -var
            literals.append(var)
        return Formula.Formula(Formula.FT.OR, literals)

    def solve(self, decisions_per_round=5):
        solution = False
        if not decisions_per_round:
            decisions_per_round -= 1
        while True:
            conflict = self._conflict()
            if conflict:
                conflict = self._explain(conflict)
                formula = self._conflict_to_formula(conflict)
                self.cdcl.learnConflict(formula)
            elif not solution:
                self._propagate()
            else:
                assignment = []
                for var in self.cdcl.partialAssignment.keys():
                    data = self.cdcl.formula.varFinder[var].data
                    value = self.cdcl.partialAssignment[var]
                    if data:
                        assignment.append([str(data), value])
                return assignment
            solution = self.cdcl.solve(decisions_per_round)
            if solution is False:
                return False

# from Formula import *
# from TUF import *
# import LP_solver as LP
from LP_solver import Arithmatics_solver as AS

# if __name__ == "__main__":
#     theory = TUF()
#     parse = Parse_SMT.parse
#     data1 = parse("a=b", theory.parse).data
#     data2 = parse("b=c", theory.parse).data
#     data3 = parse("g(f(a), b)=g(f(c), c)", theory.parse).data
#     data4 = parse("g(f(a), b)=g(f(c), d)", theory.parse).data
#     union_find = theory.union_find
#     arg1 = data1.arguments
#     arg2 = data2.arguments
#     arg3 = data3.arguments
#     arg4 = data4.arguments
#     union_find.add_equation(arg1[0], arg1[1])
#     union_find.add_equation(arg2[0], arg2[1])
#     print(union_find.are_equal(arg3[0], arg3[1]))
#     print(not union_find.are_equal(arg4[0], arg4[1]))
#     union_find.save()
#     union_find.reset()
#     print(not union_find.are_equal(arg1[0], arg1[1]))
#     union_find.load()
#     print(union_find.are_equal(arg2[0], arg2[1]))
# s = "[-x_1+x_2<=-1 && -2x_1+2x_2<=-2]||[-2x_1-2x_2<=-6 && -x_1+4x_2<=x_1]"
# theory = AS()
# smt = SMT(s, theory)
# print(smt.solve())
# print(s)