from CDCL import CDCL
import Formula
import Parse_SMT


class SMT:
    def __init__(self, smt: str, theory):
        self.theory = theory
        self.cdcl = CDCL(Parse_SMT.parse(smt, theory.parse))
        self.M = []

    def conflict(self):
        assignment = self.cdcl.partialAssignment
        var_true = []
        var_false = []
        var_unknown = []
        return self.theory.conflict(var_true, var_false)

    def propagate(self):
        pass

    def _learn(self):
        pass

    def solve(self):
        pass
