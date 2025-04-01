import random  # Импортируем модуль для работы со случайными числами

def generate_random_array(size, min_val=-100, max_val=100):
    """
    Функция для создания массива заданного размера, заполненного случайными целыми числами
    в диапазоне от min_val до max_val.
    """
    return [random.randint(min_val, max_val) for _ in range(size)] # _ для неиспользуемой переменной


def get_absolute_value(number):
    """
    Функция для вычисления модуля числа без abs().
    """
    # Если число отрицательное, инвертируем его
    return -number if number < 0 else number


def find_min_abs_element(array):
    """
    Функция для поиска минимального по модулю элемента в массиве.
    """
    # Первое число принимаем за минимальное
    min_element = array[0]
    # Вычисляем его модуль
    min_abs = get_absolute_value(min_element)

    # Перебираем все элементы, начиная со второго
    for num in array[1:]:
        # Вычисляем модуль текущего числа
        current_abs = get_absolute_value(num)
        # Если модуль текущего числа меньше найденного минимума обновляем
        if current_abs < min_abs:
            min_abs = current_abs
            # Запоминаем само число (не его модуль)
            min_element = num

    return min_element


def reverse_array(array):
    """
    Функция для вывода массива в обратном порядке.
    """
    return array[::-1]  # Переворачиваем срезом


def swap_arrays(arr1, arr2):
    """
    Функция для обмена элементами между двумя массивами.
    """
    for i in range(len(arr1)):
        arr1[i], arr2[i] = arr2[i], arr1[i]  # Меняем местами элементы


def main():
    """
    Основная функция программы, выполняющая все шаги задания.
    """
    # Шаг 1: Генерация массива A
    array_a = generate_random_array(10)

    # Шаг 2: Поиск минимального по модулю элемента в массиве A
    min_abs_a = find_min_abs_element(array_a)

    # Шаг 3: Вывод массива A в обратном порядке
    reversed_a = reverse_array(array_a)

    # Вывод результатов
    print("Исходный массив A:", array_a)
    print("Минимальный по модулю элемент A:", min_abs_a)
    print("Массив A в обратном порядке:", reversed_a)

    # Шаг 4: Генерация нового массива B
    array_b = generate_random_array(10)
    print("Исходный массив B:", array_b)

    # Шаг 5: Обмен элементами между массивами A и B
    swap_arrays(array_a, array_b)

    # Шаг 6: Вывод обновленных массивов A и B
    print("Обновленный массив A после обмена:", array_a)
    print("Обновленный массив B после обмена:", array_b)


if __name__ == "__main__":
    main()