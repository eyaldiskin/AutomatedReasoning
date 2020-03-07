from CDCL import CDCL
import Formula
from TData import *
import Parse_SMT


class SMT:
    def __init__(self, smt: str, theory):
        self.theory = theory
        self.cdcl = CDCL(Parse_SMT.parse(smt, theory.parse))
        self.M = []

    def _T_conflict(F, M):
        pass

    def _T_propagate(F, M):
        pass

    def T_learn(self):
        pass

    def solve(self):
        pass
