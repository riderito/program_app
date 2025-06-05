# triangle_func.py

# Пользовательское исключение для обозначения ошибок в сторонах треугольника
class IncorrectTriangleSides(Exception):
    """Исключение выбрасывается, если стороны не образуют допустимый треугольник."""
    pass


def get_triangle_type(a, b, c):
    """
    Определяет тип треугольника по длинам его сторон.

    Параметры:
        a, b, c (int или float): Длины сторон треугольника.

    Возвращает:
        str: Тип треугольника — 'equilateral', 'isosceles', 'nonequilateral'.

    Исключения:
        IncorrectTriangleSides: Если входные данные некорректны или не образуют треугольник.
    """

    # Проверка, что все стороны — положительные числа
    if not all(isinstance(side, (int, float)) and side > 0 for side in (a, b, c)):
        raise IncorrectTriangleSides("Стороны должны быть положительными числами.")

    # Проверка неравенства треугольника
    if a + b <= c or a + c <= b or b + c <= a:
        raise IncorrectTriangleSides("Стороны не удовлетворяют неравенству треугольника.")

    # Определение типа треугольника
    if a == b == c:
        return "equilateral"
    elif a == b or b == c or a == c:
        return "isosceles"
    else:
        return "nonequilateral"