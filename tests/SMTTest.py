import unittest
from Formula import *
# import Parse_SMT
from SMT import *
import TUF


class TestStringMethods(unittest.TestCase):

    def test_parse_one_var_no_theory(self):
        a = Formula(FT.VAR, varName="a", data="a")
        from_str = Parse_SMT.parse("a", lambda x: (x, x))
        self.assertTrue(areEqualFormulas(a, from_str))

    def test_parse_mixed_structure_no_theory(self):
        s = "[a||[b==[c>>d]]]&&![[d>>c]>>[!a&&b]]"
        a = Formula(FT.VAR, varName="a", data="a")
        b = Formula(FT.VAR, varName="b", data="b")
        c = Formula(FT.VAR, varName="c", data="c")
        d = Formula(FT.VAR, varName="d", data="d")
        formula = (a | (Formula(FT.IFF, [b, d <= c]))) & -((-a & b) <= (c <= d))
        from_str = Parse_SMT.parse(s, lambda x: (x, x))
        self.assertTrue(areEqualFormulas(formula, from_str))

    def test_explain(self):
        s = "a=b&&f(a)=f(b)"
        theory = TUF.TUF()
        smt = SMT(s, theory)
        var_true = [smt.cdcl.formula.varFinder["a=b"].data]
        var_false = [smt.cdcl.formula.varFinder["f(a)=f(b)"].data]
        conflict = theory.conflict(var_true, var_false)
        self.assertTrue(conflict)
        print(theory.explain(conflict, var_true, var_false, [1], [2]))
