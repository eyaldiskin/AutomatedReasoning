import unittest
from Formula import *
import Parse_SMT


class TestStringMethods(unittest.TestCase):

    def test_mixed_structure_no_theory(self):
        s = "[a||[b==[c>>d]]]&&![[d>>c]>>[!a&&b]]"
        a = Formula(FT.VAR, varName="a", data="a")
        b = Formula(FT.VAR, varName="b", data="b")
        c = Formula(FT.VAR, varName="c", data="c")
        d = Formula(FT.VAR, varName="d", data="d")
        formula = (a | (Formula(FT.IFF, [b, d <= c]))) & -((-a & b) <= (c <= d))
        from_str = Parse_SMT.parse(s, lambda x: (x, x))
        self.assertTrue(areEqualFormulas(formula, from_str))
