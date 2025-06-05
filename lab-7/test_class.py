# test_class.py

import pytest
from triangle_class import Triangle, IncorrectTriangleSides


def test_equilateral_triangle():
    """Тест: равносторонний треугольник"""
    t = Triangle(3, 3, 3)
    assert t.triangle_type() == "equilateral"
    assert t.perimeter() == 9


def test_isosceles_triangle():
    """Тест: равнобедренный треугольник"""
    t = Triangle(5, 5, 3)
    assert t.triangle_type() == "isosceles"
    assert t.perimeter() == 13


def test_nonequilateral_triangle():
    """Тест: разносторонний треугольник"""
    t = Triangle(4, 5, 6)
    assert t.triangle_type() == "nonequilateral"
    assert t.perimeter() == 15


@pytest.mark.parametrize("a, b, c", [
    (0, 1, 1),         # нулевая сторона
    (-1, 2, 2),        # отрицательная сторона
    (1, 2, 3),         # нарушение неравенства треугольника
    ("x", 2, 2),       # нечисловое значение
])
def test_invalid_triangle_inputs(a, b, c):
    """Негативные тесты: некорректные стороны"""
    with pytest.raises(IncorrectTriangleSides):
        Triangle(a, b, c)