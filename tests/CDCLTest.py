import unittest
from Formula import Formula, FT, areEquivalentFormulas
from CDCL import CDCL


class TestCDCL(unittest.TestCase):

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

    def test_CDCL_init_no_exception(self):
        try:
            form = self.var0 & self.var1
            solver = CDCL(form)

        except Exception as e:
            self.fail(str(e))

    def test_CDCL_solve_no_exception(self):
        try:
            form = self.var0 & self.var1
            solver = CDCL(form)
            solver.solve()

        except Exception as e:
            self.fail(str(e))

    def test_CDCL_solve_1(self):
        form = self.var0 & self.var1
        solver = CDCL(form)
        out = solver.solve()
        self.assertTrue(out)
        self.assertTrue(solver.partialAssignment["var0"])
        self.assertTrue(solver.partialAssignment["var1"])

    def test_CDCL_solve_2(self):
        form = self.var0 & -self.var0
        solver = CDCL(form)
        out = solver.solve()
        self.assertFalse(out)

    def test_CDCL_solve_3(self):
        form = (self.var0 | self.var1) & (-self.var0 | -
                                          self.var1) & (self.var0 | -self.var1)
        solver = CDCL(form)
        out = solver.solve()
        self.assertTrue(out)
        self.assertTrue(solver.partialAssignment["var0"])
        self.assertFalse(solver.partialAssignment["var1"])

    def test_CDCL_solve_4(self):
        form = Formula(FT.IFF, [self.var0, self.var1]) & Formula(
            FT.IFF, [self.var2, self.var3])
        solver = CDCL(form)
        out = solver.solve()
        self.assertTrue(out)
        self.assertEqual(
            solver.partialAssignment["var0"], solver.partialAssignment["var1"])
        self.assertEqual(
            solver.partialAssignment["var2"], solver.partialAssignment["var3"])

    def test_CDCL_solve_5(self):
        form = (self.var0 | self.var1) & (self.var2 | self.var3 | self.var4) & (
            (self.var1 & self.var3) | (self.var4 <= self.var0 <= self.var1)) & (-self.var0 | -self.var1 | -self.var2) & (self.var4 | self.var0) & (-self.var4 |-self.var3)
        solver = CDCL(form)
        out = solver.solve()
        print()

    def test_CDCL_solve_6(self):
        form = (self.var0 | self.var1) & (self.var2 | self.var3 | self.var4) & (
            (self.var1 & self.var3) | (self.var4 <= self.var0 <= self.var1)) & (-self.var0 | -self.var1 | -self.var2) & (self.var4 | self.var0) & (-self.var4 |-self.var3)& (-self.var0|self.var3) 
        solver = CDCL(form)
        out = solver.solve()
        print()

    def test_CDCL_100_vars(self):
        form = Formula(FT.VAR,varName="var0")
        for i in range(1,100):
            form = form & Formula(FT.VAR,varName="var"+str(i))
        solver = CDCL(form)
        out = solver.solve()
        assignment = solver.getAssignment()
        print()

        


if __name__ == '__main__':
    unittest.main()
