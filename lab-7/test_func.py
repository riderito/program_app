# test_func.py

import unittest
from triangle_func import get_triangle_type, IncorrectTriangleSides


class TestGetTriangleType(unittest.TestCase):
    """
    Набор юнит-тестов для функции get_triangle_type.
    """

    def test_equilateral_triangle(self):
        """Тест: все стороны равны (равносторонний треугольник)"""
        self.assertEqual(get_triangle_type(3, 3, 3), "equilateral")

    def test_isosceles_triangle(self):
        """Тест: две стороны равны (равнобедренный треугольник)"""
        self.assertEqual(get_triangle_type(4, 4, 5), "isosceles")

    def test_nonequilateral_triangle(self):
        """Тест: все стороны разные (разносторонний треугольник)"""
        self.assertEqual(get_triangle_type(5, 6, 7), "nonequilateral")

    def test_zero_side(self):
        """Тест: одна из сторон равна нулю"""
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(0, 4, 5)

    def test_negative_side(self):
        """Тест: одна из сторон отрицательная"""
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(-1, 2, 2)

    def test_triangle_inequality_violation(self):
        """Тест: нарушение неравенства треугольника"""
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(1, 2, 3)

    def test_non_numeric_input(self):
        """Тест: входные данные не являются числами"""
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type("a", 2, 2)


if __name__ == '__main__':
    unittest.main()