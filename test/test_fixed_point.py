import unittest
import warnings

from PyFxP.fix_point import FixedPoint
from PyFxP.registry import Registry


class TestFixedPoint(unittest.TestCase):

    def test_from_float_unsigned(self):
        fxp = FixedPoint(3.75, int_width=4, fract_width=4, signed=False)
        self.assertEqual(fxp.val_int, 60)
        self.assertAlmostEqual(fxp.val_float, 3.75, places=6)
        self.assertEqual(fxp.val_bin, "00111100")

    def test_from_float_signed(self):
        fxp = FixedPoint(-1.5, int_width=3, fract_width=4, signed=True)
        self.assertEqual(fxp.val_int, -24)
        self.assertAlmostEqual(fxp.val_float, -1.5, places=6)
        self.assertEqual(fxp.val_bin, "11101000")

    def test_from_int_unsigned(self):
        fxp = FixedPoint(60, int_width=4, fract_width=4, signed=False)
        self.assertAlmostEqual(fxp.val_float, 3.75, places=6)
        self.assertEqual(fxp.val_bin, "00111100")

    def test_from_bin_unsigned(self):
        fxp = FixedPoint("00111100", int_width=4, fract_width=4, signed=False)
        self.assertEqual(fxp.val_int, 60)
        self.assertAlmostEqual(fxp.val_float, 3.75, places=6)

    def test_from_bin_signed_negative(self):
        fxp = FixedPoint("11101000", int_width=3, fract_width=4, signed=True)
        self.assertEqual(fxp.val_int, -24)
        self.assertAlmostEqual(fxp.val_float, -1.5, places=6)

    def test_invalid_bin_length(self):
        with self.assertRaises(ValueError):
            FixedPoint("101010", int_width=4, fract_width=4, signed=False)

    def test_wide_unsigned(self):
        fxp = FixedPoint(255.5, int_width=8, fract_width=4, signed=False)
        self.assertEqual(fxp.val_int, 255 * 16 + 8)
        self.assertAlmostEqual(fxp.val_float, 255.5, places=6)

    def test_wide_signed_negative(self):
        fxp = FixedPoint(-32.75, int_width=6, fract_width=2, signed=True)
        self.assertEqual(fxp.val_int, -131)
        self.assertAlmostEqual(fxp.val_float, -32.75, places=6)

    def test_small_width(self):
        fxp = FixedPoint(1.25, int_width=1, fract_width=2, signed=False)
        self.assertEqual(fxp.val_int, 5)
        self.assertEqual(fxp.val_bin, "101")
        self.assertAlmostEqual(fxp.val_float, 1.25, places=6)

    def test_clip_overflow_unsigned(self):
        fxp = FixedPoint(300.0, int_width=4, fract_width=4, signed=False)
        self.assertEqual(fxp.val_int, 255)  # clipped
        self.assertAlmostEqual(fxp.val_float, 15.9375, places=6)

    def test_clip_overflow_signed(self):
        fxp = FixedPoint(100.0, int_width=5, fract_width=2, signed=True)
        self.assertEqual(fxp.val_int, 127)
        self.assertAlmostEqual(fxp.val_float, 31.75, places=6)

    def test_clip_underflow_signed(self):
        fxp = FixedPoint(-100.0, int_width=5, fract_width=2, signed=True)
        self.assertEqual(fxp.val_int, -128)
        self.assertAlmostEqual(fxp.val_float, -32.0, places=6)

    def test_zero_signed(self):
        fxp = FixedPoint(0.0, int_width=3, fract_width=5, signed=True)
        self.assertEqual(fxp.val_int, 0)
        self.assertEqual(fxp.val_bin, "000000000")
        self.assertEqual(fxp.val_float, 0.0)

    def test_zero_unsigned(self):
        fxp = FixedPoint(0.0, int_width=3, fract_width=5, signed=False)
        self.assertEqual(fxp.val_int, 0)
        self.assertEqual(fxp.val_bin, "00000000")
        self.assertEqual(fxp.val_float, 0.0)

    def test_negative_small_signed(self):
        fxp = FixedPoint(-0.25, int_width=1, fract_width=3, signed=True)
        self.assertEqual(fxp.val_int, -2)
        self.assertEqual(fxp.val_bin, "11110")
        self.assertAlmostEqual(fxp.val_float, -0.25, places=6)

    def test_negative_exact_boundary(self):
        # max negative value: -2^(int_width)
        fxp = FixedPoint(-4.0, int_width=2, fract_width=2, signed=True)
        self.assertEqual(fxp.val_int, -16)
        self.assertEqual(fxp.val_bin, "10000")
        self.assertAlmostEqual(fxp.val_float, -4.0, places=6)

    def test_negative_overflow_clipping(self):
        fxp = FixedPoint(-100.0, int_width=3, fract_width=3, signed=True)
        # min_val = -64 => int = -64 => float = -8.0
        self.assertEqual(fxp.val_int, -64)
        self.assertAlmostEqual(fxp.val_float, -8.0, places=6)

    def test_negative_from_bin(self):
        fxp = FixedPoint("11111100", int_width=3, fract_width=4, signed=True)
        self.assertEqual(fxp.val_int, -4)
        self.assertAlmostEqual(fxp.val_float, -0.25, places=6)

    def test_add_unsigned(self):
        a = FixedPoint(7.5, int_width=3, fract_width=4, signed=False)
        b = FixedPoint(1.0, int_width=3, fract_width=4, signed=False)
        c = a + b
        self.assertAlmostEqual(c.val_float, 8.5, places=6)
        self.assertEqual(c.val_int, 136)
        self.assertEqual(c.val_bin, "10001000")  
        self.assertEqual(c.int_width, 4)
        self.assertEqual(c.fract_width, 4)
        self.assertFalse(c.signed)

    def test_add_unsigned(self):
        a = FixedPoint(7.5, int_width=3, fract_width=4, signed=False)
        b = FixedPoint(1.0, int_width=3, fract_width=4, signed=False)
        c = a + b
        self.assertAlmostEqual(c.val_float, 8.5, places=6)
        self.assertEqual(c.val_int, 136)
        self.assertEqual(c.val_bin, "10001000")  
        self.assertEqual(c.int_width, 4)
        self.assertEqual(c.fract_width, 4)
        self.assertFalse(c.signed)

    def test_add_signed(self):
        a = FixedPoint(-2.0, int_width=3, fract_width=4, signed=True)
        b = FixedPoint(1.25, int_width=3, fract_width=4, signed=True)
        c = a + b
        self.assertAlmostEqual(c.val_float, -0.75, places=6)
        self.assertEqual(c.val_int, -12)
        self.assertEqual(c.val_bin, "111110100") 
        self.assertEqual(c.int_width, 4)
        self.assertTrue(c.signed)

    def test_add_signed_unsigned(self):
        a = FixedPoint(3.0, int_width=3, fract_width=4, signed=False)
        b = FixedPoint(-1.0, int_width=3, fract_width=4, signed=True)
        c = a + b
        self.assertAlmostEqual(c.val_float, 2.0, places=6)
        self.assertEqual(c.val_int, 32)
        self.assertEqual(c.val_bin, "000100000") 
        self.assertEqual(c.int_width, 4)
        self.assertTrue(c.signed)

    def test_sub_unsigned_positive_result(self):
        a = FixedPoint(7.0, int_width=3, fract_width=4, signed=False)
        b = FixedPoint(2.5, int_width=3, fract_width=4, signed=False)
        c = a - b
        self.assertAlmostEqual(c.val_float, 4.5, places=6)
        self.assertEqual(c.val_int, 72)
        self.assertEqual(c.val_bin, "01001000") 
        self.assertEqual(c.int_width, 4)
        self.assertFalse(c.signed)

    def test_sub_unsigned_negative_result(self):
        a = FixedPoint(2.0, int_width=3, fract_width=4, signed=False)
        b = FixedPoint(4.5, int_width=3, fract_width=4, signed=False)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            c = a - b

            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[0].category, RuntimeWarning))
            self.assertIn("underflow", str(w[0].message).lower())

        self.assertEqual(c.val_float, 0)
        self.assertEqual(c.val_int, 0)
        self.assertEqual(c.val_bin, "00000000")  
        self.assertEqual(c.int_width, 4)
        self.assertFalse(c.signed)

    def test_sub_signed(self):
        a = FixedPoint(-1.5, int_width=3, fract_width=4, signed=True)
        b = FixedPoint(-1.5, int_width=3, fract_width=4, signed=True)
        c = a - b
        self.assertAlmostEqual(c.val_float, 0.0, places=6)
        self.assertEqual(c.val_int, 0)
        self.assertEqual(c.val_bin, "000000000") 
        self.assertEqual(c.int_width, 4)
        self.assertTrue(c.signed)

    def test_mul_unsigned(self):
        a = FixedPoint(2.0, int_width=3, fract_width=4, signed=False)
        b = FixedPoint(1.5, int_width=3, fract_width=4, signed=False)
        c = a * b
        self.assertAlmostEqual(c.val_float, 3.0, places=6)
        self.assertEqual(c.val_int, 768)
        self.assertEqual(c.val_bin, "00001100000000") 
        self.assertEqual(c.int_width, 6)
        self.assertEqual(c.fract_width, 8)
        self.assertFalse(c.signed)

    def test_mul_signed(self):
        a = FixedPoint(-2.0, int_width=3, fract_width=4, signed=True)
        b = FixedPoint(1.5, int_width=3, fract_width=4, signed=True)
        c = a * b
        self.assertAlmostEqual(c.val_float, -3.0, places=6)
        self.assertEqual(c.val_int, -768)
        self.assertEqual(c.val_bin, "1111110100000000")  
        self.assertEqual(c.int_width, 7)
        self.assertEqual(c.fract_width, 8)
        self.assertTrue(c.signed)

    def test_mul_signed_unsigned(self):
        a = FixedPoint(3.0, int_width=3, fract_width=4, signed=False)
        b = FixedPoint(-2.0, int_width=3, fract_width=4, signed=True)
        c = a * b
        self.assertAlmostEqual(c.val_float, -6.0, places=6)
        self.assertEqual(c.val_int, -1536)
        self.assertEqual(c.val_bin, "111101000000000")  
        self.assertEqual(c.int_width, 6)
        self.assertEqual(c.fract_width, 8)
        self.assertTrue(c.signed)

    def test_mul_zero(self):
        a = FixedPoint(0.0, int_width=3, fract_width=4, signed=True)
        b = FixedPoint(5.25, int_width=3, fract_width=4, signed=True)
        c = a * b
        self.assertEqual(c.val_int, 0)
        self.assertEqual(c.val_float, 0.0)
        self.assertEqual(c.val_bin, "0000000000000000") 

    def test_mul_negative_negative(self):
        a = FixedPoint(-1.5, int_width=3, fract_width=4, signed=True)
        b = FixedPoint(-2.0, int_width=3, fract_width=4, signed=True)
        c = a * b
        self.assertAlmostEqual(c.val_float, 3.0, places=6)
        self.assertEqual(c.val_int, 768)
        self.assertEqual(c.val_bin, "0000001100000000") 
        self.assertTrue(c.signed)

    def test_lshift_unsigned(self):
        a = FixedPoint(1.5, int_width=3, fract_width=4, signed=False)   # 0011000 -> 0110000
        b = a << 1
        self.assertEqual(b.val_float, 3.0)
        self.assertEqual(b.val_int, 48)
        self.assertEqual(b.val_bin, "0110000") 
        self.assertFalse(b.signed)

    def test_lshift_signed(self):
        a = FixedPoint(-3.5, int_width=3, fract_width=4, signed=True)   # 11001000 -> 10010000
        print(a.val_bin)
        b = a << 1
        self.assertEqual(b.val_float, -7)
        self.assertEqual(b.val_int, -112)
        self.assertEqual(b.val_bin, "10010000") 
        self.assertTrue(b.signed)

    def test_rshift_unsigned(self):
        a = FixedPoint(3.0, int_width=3, fract_width=4, signed=False)  # 0110000 -> 0011000
        b = a >> 1
        self.assertAlmostEqual(b.val_float, 1.5, places=6)
        self.assertEqual(b.val_int, 24)
        self.assertEqual(b.val_bin, "0011000")
        self.assertFalse(b.signed)

    def test_rshift_signed(self):
        a = FixedPoint(-4.0, int_width=3, fract_width=4, signed=True)  # 11000000 -> 11100000 (arithmetic shift)
        b = a >> 1
        self.assertAlmostEqual(b.val_float, -2.0, places=6)
        self.assertEqual(b.val_int, -32)
        self.assertEqual(b.val_bin, "11100000")
        self.assertTrue(b.signed)

if __name__ == "__main__":
    unittest.main()
