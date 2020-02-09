import unittest
from Formula import Formula, FT, areEquivalentFormulas


class TestStringMethods(unittest.TestCase):

    def setUp(self):
        self.var0 = Formula(FT.VAR, varName="var0")
        self.var1 = Formula(FT.VAR, varName="var1")
        self.var2 = Formula(FT.VAR, varName="var2")
        self.var3 = Formula(FT.VAR, varName="var3")
        self.var4 = Formula(FT.VAR, varName="var4")
        self.var5 = Formula(FT.VAR, varName="var5")
        self.var6 = Formula(FT.VAR, varName="var6")
        self.var7 = Formula(FT.VAR, varName="var7")
        self.var8 = Formula(FT.VAR, varName="var8")
        self.var9 = Formula(FT.VAR, varName="var9")

    def test_formula_equivalent_to_itself_1(self):
        formula = self.var0
        self.assertTrue(areEquivalentFormulas(formula, formula))

    def test_formula_equivalent_1(self):

        implicit = self.var2 <= self.var1
        explicit = -self.var1 | self.var2
        self.assertTrue(areEquivalentFormulas(implicit, explicit))


if __name__ == '__main__':
    unittest.main()
