# triangle_class.py

class IncorrectTriangleSides(Exception):
    """Исключение выбрасывается, если стороны не образуют допустимый треугольник."""
    pass


class Triangle:
    """
    Класс, представляющий треугольник по длинам его сторон.
    """

    def __init__(self, a, b, c):
        """
        Конструктор класса.

        Параметры:
            a, b, c (int или float): Длины сторон треугольника.

        Исключения:
            IncorrectTriangleSides: если данные некорректны.
        """
        if not all(isinstance(side, (int, float)) and side > 0 for side in (a, b, c)):
            raise IncorrectTriangleSides("Стороны должны быть положительными числами.")

        if a + b <= c or a + c <= b or b + c <= a:
            raise IncorrectTriangleSides("Стороны не удовлетворяют неравенству треугольника.")

        self.a = a
        self.b = b
        self.c = c

    def triangle_type(self):
        """
        Определяет тип треугольника.

        Возвращает:
            str: 'equilateral', 'isosceles' или 'nonequilateral'
        """
        if self.a == self.b == self.c:
            return "equilateral"
        elif self.a == self.b or self.b == self.c or self.a == self.c:
            return "isosceles"
        return "nonequilateral"

    def perimeter(self):
        """
        Вычисляет периметр треугольника.

        Возвращает:
            float: сумма длин сторон
        """
        return self.a + self.b + self.c