import unittest
import SAT
import boolean

algebra = boolean.BooleanAlgebra()


class TestSATMethods(unittest.TestCase):

    def test_Preprocess_1(self):
        x, y = algebra.symbols("x", "y")
        self.assertTrue(SAT.preproccess(x & y) == (x & y))

    def test_Preprocess_2(self):
        x, y = algebra.symbols("x", "y")
        self.assertTrue(SAT.preproccess((x | ~x) & (x | y)) == (x | y))



if __name__ == '__main__':
    unittest.main()
