import unittest
from Formula import *
from SMT import *
from TUF import *


class TestStringMethods(unittest.TestCase):

    def test_parse_one_var_no_theory(self):
        a = Formula(FT.VAR, varName="a", data="a")
        from_str = Parse_SMT.parse("a", lambda x: (x, x))
        self.assertTrue(areEqualFormulas(a, from_str))

    def test_parse_mixed_structure_no_theory1(self):
        s = "~[a||[b= =[c>>d] ]]&&~[[d>>c]>>[~a &&b]]"
        a = Formula(FT.VAR, varName="a", data="a")
        b = Formula(FT.VAR, varName="b", data="b")
        c = Formula(FT.VAR, varName="c", data="c")
        d = Formula(FT.VAR, varName="d", data="d")
        formula = -(a | (Formula(FT.IFF, [b, d <= c]))) & -((-a & b) <= (c <= d))
        from_str = Parse_SMT.parse(s, lambda x: (x, x))
        self.assertTrue(areEqualFormulas(formula, from_str))

    def test_parse_mixed_structure_no_theory2(self):
        s = "~[ [a||[ b==[c>>d]]]&& ~[[d>>c]>>[~a&&b]]]"
        a = Formula(FT.VAR, varName="a", data="a")
        b = Formula(FT.VAR, varName="b", data="b")
        c = Formula(FT.VAR, varName="c", data="c")
        d = Formula(FT.VAR, varName="d", data="d")
        formula = -((a | (Formula(FT.IFF, [b, d <= c]))) & -((-a & b) <= (c <= d)))
        from_str = Parse_SMT.parse(s, lambda x: (x, x))
        self.assertTrue(areEqualFormulas(formula, from_str))

    def test_congruence(self):
        theory = TUF()
        parse = Parse_SMT.parse
        data1 = parse("a=b", theory.parse).data
        data2 = parse("b=c", theory.parse).data
        data3 = parse("g(f(a), b)=g(f(c), c)", theory.parse).data
        data4 = parse("g(f(a), b)=g(f(c), d)", theory.parse).data
        union_find = theory.union_find
        arg1 = data1.arguments
        arg2 = data2.arguments
        arg3 = data3.arguments
        arg4 = data4.arguments
        union_find.add_equation(arg1[0], arg1[1])
        union_find.add_equation(arg2[0], arg2[1])
        self.assertTrue(union_find.are_equal(arg3[0], arg3[1]))
        self.assertTrue(not union_find.are_equal(arg4[0], arg4[1]))
        union_find.save()
        union_find.reset()
        self.assertTrue(not union_find.are_equal(arg1[0], arg1[1]))
        union_find.load()
        self.assertTrue(union_find.are_equal(arg2[0], arg2[1]))

    def test_explain(self):
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
