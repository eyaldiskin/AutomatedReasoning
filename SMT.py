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

    def _conflict(self):
        var_true, var_false = self._get_assigned_vars()
        conflict = self.theory.conflict(var_true, var_false)
        if conflict:
            formula = self.cdcl.formula  # todo return to variables?
            clause_vars = []
            for l in conflict:
                for var_name in formula.variables:
                    var = formula.varFinder[var_name]
                    if var.data == l[0]:
                        clause_vars.append([var, l[1]])
                        break
            return clause_vars
        return None

    def propagate(self):
        pass

    def _learn(self):
        pass

    def solve(self):
        pass
