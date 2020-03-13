import unittest
from Formula import *
from SMT import *
from TUF import *
import LP_solver as LP
from LP_solver import Arithmatics_solver as AS


class TestStringMethods(unittest.TestCase):

    def test_parse_one_var_no_theory(self):
        formula = Formula.Formula(FT.VAR, varName="a", data="a")
        from_str = Parse_SMT.parse("a", lambda x: (x, x))
        self.assertTrue(formula == from_str)

    def test_parse_mixed_structure_no_theory1(self):
        s = "~[a||[b==[c>>d]]]&&~[[d>>c]>>[~a&&b]]"
        a = Formula.Formula(FT.VAR, varName="a", data="a")
        b = Formula.Formula(FT.VAR, varName="b", data="b")
        c = Formula.Formula(FT.VAR, varName="c", data="c")
        d = Formula.Formula(FT.VAR, varName="d", data="d")
        formula = -(a | (Formula.Formula(FT.IFF, [b, d <= c]))) & -((-a & b) <= (c <= d))
        from_str = Parse_SMT.parse(s, lambda x: (x, x))
        self.assertTrue(formula == from_str)

    def test_parse_mixed_structure_no_theory2(self):
        s = "~[[a||[b==[c>>d]]]&&~[[d>>c]>>[~a&&b]]]"
        a = Formula.Formula(FT.VAR, varName="a", data="a")
        b = Formula.Formula(FT.VAR, varName="b", data="b")
        c = Formula.Formula(FT.VAR, varName="c", data="c")
        d = Formula.Formula(FT.VAR, varName="d", data="d")
        formula = -((a | (Formula.Formula(FT.IFF, [b, d <= c]))) & -((-a & b) <= (c <= d)))
        from_str = Parse_SMT.parse(s, lambda x: (x, x))
        self.assertTrue(formula == from_str)

    def test_parse_TUF(self):
        s = "[[~f(x)=b]&&x=f(b)]||b=f(x)"
        from_str = Parse_SMT.parse(s, TUF().parse)
        x = UFData(UFType.VAR, "x")
        fx = UFData(UFType.FOO, "f", [x])
        b = UFData(UFType.VAR, "b")
        fb = UFData(UFType.FOO, "f", [b])
        eq1 = Formula.Formula(FT.VAR, varName="f(x)=b", data=UFData(UFType.PRED, "=", [fx, b]))
        eq2 = Formula.Formula(FT.VAR, varName="x=f(b)", data=UFData(UFType.PRED, "=", [x, fb]))
        formula = ((-eq1) & eq2) | eq1
        self.assertTrue(formula == from_str)
        for var in formula.variables:
            self.assertTrue(formula.varFinder[var].data == from_str.varFinder[var].data)

    def test_parse_LP(self):
        s = "[-x_1+x_2<=-1 && -2x_1+2x_2<=-2]||[-2x_1-2x_2<=-6 && -x_1+4x_2<=x_1]"
        from_str = Parse_SMT.parse(s, AS().parse)
        eq1 = Formula.Formula(FT.VAR, varName="+ (-1.0x_1) + (1.0x_2) <=  -1.0", data=LP.equstion("-x_1+x_2<=-1"))
        eq2 = Formula.Formula(FT.VAR, varName="+ (-1.0x_1) + (1.0x_2) <=  -1.0", data=LP.equstion("-2x_1+2x_2<=-2"))
        name3 = "+ (-0.3333333333333333x_1) + (-0.3333333333333333x_2) <=  -1.0"
        eq3 = Formula.Formula(FT.VAR, varName=name3, data=LP.equstion("-2x_1-2x_2<=-6"))
        eq4 = Formula.Formula(FT.VAR, varName="+ (-2.0x_1) + (4.0x_2) <=  0.0", data=LP.equstion("-x_1+4x_2<=x_1"))
        formula = (eq1 & eq2) | (eq3 & eq4)
        self.assertTrue(formula == from_str)
        for var in formula.variables:
            self.assertTrue(formula.varFinder[var].data == from_str.varFinder[var].data)

    def test_union_find(self):
        # preprocess
        theory = TUF()
        parse = Parse_SMT.parse
        data1 = parse("a=b", theory.parse).data
        data2 = parse("b=c", theory.parse).data
        data3 = parse("g(f(a), b)=g(f(c), c)", theory.parse).data
        data4 = parse("g(f(a), b)=g(f(c), d)", theory.parse).data
        union_find = theory.union_find
        arg1, arg2 = data1.arguments, data2.arguments
        arg3, arg4 = data3.arguments, data4.arguments

        # test
        union_find.add_equation(arg1[0], arg1[1])
        union_find.add_equation(arg2[0], arg2[1])
        self.assertTrue(union_find.are_equal(arg3[0], arg3[1]))
        self.assertTrue(not union_find.are_equal(arg4[0], arg4[1]))
        union_find.save()
        union_find.reset()
        self.assertTrue(not union_find.are_equal(arg1[0], arg1[1]))
        union_find.load()
        self.assertTrue(union_find.are_equal(arg2[0], arg2[1]))

    def test_explain_TUF(self):
        s = "a=b&&f(a)=f(c)&&b=c&&g(f(a))=g(f(c))"
        theory = TUF()
        smt = SMT(s, theory)
        var_true = [smt.cdcl.formula.varFinder["a=b"].data, smt.cdcl.formula.varFinder["b=c"].data,
                    smt.cdcl.formula.varFinder["g(f(a))=g(f(c))"].data]
        var_false = [smt.cdcl.formula.varFinder["f(a)=f(c)"].data]
        conflict = theory.conflict(var_true, var_false)
        self.assertTrue(conflict)
        exp = theory.explain(conflict, var_true, var_false, [1, 4, 5], [2])
        my_exp = [[x, False] for x in var_true[:-1]]
        my_exp.append([smt.cdcl.formula.varFinder["f(a)=f(c)"].data, True])
        self.assertTrue(exp == my_exp)

    def test_basic_TUF_solve(self):
        s = "a=b&&b=c&&c=a"
        theory = TUF()
        smt = SMT(s, theory)
        self.assertTrue(smt.solve() == [['a=b', True], ['b=c', True], ['c=a', True]])

    def test_basic_TUF_conflict(self):
        s = "a=b&&b=c&&~c=a"
        theory = TUF()
        smt = SMT(s, theory)
        self.assertTrue(not smt.solve())

    def test_TUF_solve(self):
        s = "a=b&&f(a)=f(c)&&~b=c&&g(f(a))=g(f(c))"
        theory = TUF()
        smt = SMT(s, theory)
        solution = [['a=b', True], ['f(a)=f(c)', True], ['b=c', False], ['g(f(a))=g(f(c))', True]]
        self.assertTrue(smt.solve() == solution)

    def test_TUF_conflict1(self):
        s = "mul(a,add(abs(b),c))=d&&~mul(b,add(abs(a),c))=d&&a=b"
        theory = TUF()
        smt = SMT(s, theory)
        self.assertTrue(not smt.solve())

    def test_TUF_conflict2(self):
        s = "g(a)=c&&[~f(g(a))=f(c)||g(a)=d]&&~c=d"
        theory = TUF()
        smt = SMT(s, theory)
        self.assertTrue(not smt.solve())

    def test_TUF_conflict3(self):
        s = "f(f(f(a)))=a&&f(f(f(f(f(a)))))=a&&~f(a)=a"
        theory = TUF()
        smt = SMT(s, theory)
        self.assertTrue(not smt.solve())

    def test_basic_LP(self):
        s = "[-x_1+x_2<=-1 && -2x_1+2x_2<=-2]||[-2x_1-2x_2<=-6 && -x_1+4x_2<=x_1]"
        theory = AS()
        smt = SMT(s, theory)
        self.assertTrue(smt.solve())

    def test_LP_conflict(self):
        s = "x_1+x_2+2x_3<=4&&2x_1+3x_3<=5&&2x_1+x_2+3x_3<=7&&-3x_1-2x_2-4x_3<=-10"
        theory = AS()
        smt = SMT(s, theory)
        self.assertTrue(not smt.solve())


if __name__ == '__main__':
    unittest.main()
