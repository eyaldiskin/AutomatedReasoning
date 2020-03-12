import unittest
from Formula import Formula, FT, areEquivalentFormulas


class TestFormula(unittest.TestCase):

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

    def test_flatten_1(self):
        and1 = self.var0 & self.var1
        and2 = self.var2 & and1
        and2flat = self.var2 & and1
        and2flat.flatten()
        self.assertTrue(areEquivalentFormulas(and2, and2flat))
        self.assertTrue(len(and2flat.formulas) is 3)

    def test_flatten_2(self):
        and1 = self.var0 & self.var1
        and2 = self.var2 & self.var3
        and3 = and1 & and2
        and3flat = and1 & and2
        and3flat.flatten()
        self.assertTrue(areEquivalentFormulas(and3, and3flat))
        self.assertTrue(len(and3flat.formulas) is 4)

    def test_cnf_1(self):
        try:
            self.var0.toCNF()
        except Exception as e:
            self.fail(str(e))

    def test_nnf_1(self):
        try:
            self.var0.toNNF()
        except Exception as e:
            self.fail(str(e))

    def test_tseitlin_1(self):
        try:
            form = self.var0 & self.var1
            form.toTseitlin()
            print(form.toString())
        except Exception as e:
            self.fail(str(e))  
        


if __name__ == '__main__':
    unittest.main()
