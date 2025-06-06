# Импортируем библиотеку pytest для написания тестов
import pytest

# Импортируем класс Triangle и исключение IncorrectTriangleSides из модуля triangle_class
from triangle_class import Triangle, IncorrectTriangleSides


def test_equilateral_triangle():
    # Тест: равносторонний треугольник
    t = Triangle(3, 3, 3)

    # Проверяем тип треугольника
    assert t.triangle_type() == "equilateral"

    # Проверяем правильность вычисления периметра
    assert t.perimeter() == 9


def test_isosceles_triangle():
    # Тест: равнобедренный треугольник
    t = Triangle(5, 5, 3)

    # Проверяем тип треугольника
    assert t.triangle_type() == "isosceles"

    # Проверяем правильность вычисления периметра
    assert t.perimeter() == 13


def test_nonequilateral_triangle():
    # Тест: разносторонний треугольник
    t = Triangle(4, 5, 6)

    # Проверяем тип треугольника
    assert t.triangle_type() == "nonequilateral"

    # Проверяем правильность вычисления периметра
    assert t.perimeter() == 15


# Используем параметризацию для проверки разных некорректных входных данных
@pytest.mark.parametrize("a, b, c", [
    (0, 1, 1),  # Нулевая сторона — невалидно
    (-1, 2, 2),  # Отрицательная сторона — невалидно
    (1, 2, 3),  # Нарушение неравенства треугольника — невалидно
    ("x", 2, 2),  # Нечисловое значение — невалидно
])
def test_invalid_triangle_inputs(a, b, c):
    # Негативные тесты: некорректные стороны

    # Ожидаем возбуждение исключения при создании треугольника с некорректными сторонами
    with pytest.raises(IncorrectTriangleSides):
        Triangle(a, b, c)


