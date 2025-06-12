import unittest
from PyFxP.fix_point import FixedPoint
from PyFxP.registry import Registry, OppType, Opp


class TestRegistry(unittest.TestCase):

    def setUp(self):
        # Clear registry before each test
        Registry.var_registry.clear()
        Registry.op_registry.clear()

    def test_log_var(self):
        fxp = FixedPoint(1.5, int_width=3, fract_width=4, signed=False)
        self.assertEqual(len(Registry.var_registry), 1)
        self.assertIs(Registry.var_registry[0], fxp)

    def test_log_op_add(self):
        a = FixedPoint(2.0, 3, 4, signed=True)
        b = FixedPoint(1.0, 3, 4, signed=True)
        result = a + b
        self.assertEqual(len(Registry.op_registry), 1)

        op = Registry.op_registry[0]
        self.assertIsInstance(op, Opp)
        self.assertEqual(op.lhs, a)
        self.assertEqual(op.rhs, b)
        self.assertEqual(op.result, result)
        self.assertEqual(op.opp_type, OppType.__ADD__)

    def test_log_op_sub(self):
        a = FixedPoint(2.5, 3, 4, signed=False)
        b = FixedPoint(1.0, 3, 4, signed=False)
        result = a - b
        self.assertEqual(Registry.op_registry[0].opp_type, OppType.__SUB__)

    def test_log_op_mul(self):
        a = FixedPoint(1.5, 3, 4, signed=True)
        b = FixedPoint(2.0, 3, 4, signed=False)
        result = a * b
        self.assertEqual(Registry.op_registry[0].opp_type, OppType.__MUL__)


if __name__ == "__main__":
    unittest.main()
