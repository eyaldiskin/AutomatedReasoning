from CDCL import CDCL
# import Formula
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
            if data == formula.varFinder[var_name].data:
                return var_name
        return None

    def _conflict(self):
        var_true, var_false = self._get_assigned_vars()
        return self.theory.conflict(var_true, var_false)

    def _propagate(self):
        while True:
            var_true, var_false, var_unknown = self._get_part_assignment()
            new_vars = self.theory.propagate(var_true, var_false, var_unknown)
            if not new_vars:
                break
            for var in new_vars:
                data, assignment = var
                var_name = self._get_var_name_by_data(data)
                # todo insert to cdcl...

    def _explain(self, conflict):
        var_true, var_false = self._get_assigned_vars()
        # todo get levels
        true_lvls = []
        false_lvls = []
        new_conflict = self.theory.explain(conflict, var_true, var_false, true_lvls, false_lvls)
        while new_conflict != conflict:
            conflict = new_conflict
            new_conflict = self.theory.explain(conflict, var_true, var_false, true_lvls, false_lvls)
        return new_conflict

    def solve(self, decisions_per_round=5):
        solution = False
        if not decisions_per_round:
            decisions_per_round -= 1
        while True:
            conflict = self._conflict()
            if conflict:
                conflict = self._explain(conflict)
                # todo finish branch
            elif not solution:
                self._propagate()
            else:
                pass
                # todo return the assignment
            solution = self.cdcl.solve(decisions_per_round)
            if solution is False:
                return False

#
# from TUF import *
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
