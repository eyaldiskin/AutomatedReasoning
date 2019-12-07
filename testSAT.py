import unittest
import SAT


class TestSATMethods(unittest.TestCase):

    def test_1(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_2(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_3(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)


if __name__ == '__main__':
    unittest.main()
