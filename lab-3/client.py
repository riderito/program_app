# Для выполнения HTTP-запросов
import requests
# Для генерации случайных чисел
import random


def perform_operations():
    """
    Функция для выполнения операций с API.
    Последовательно выполняет GET, POST и DELETE запросы к API,
    формирует математическое выражение из полученных результатов,
    вычисляет и выводит итоговый результат.
    """
    # Выполнение GET-запроса
    # Случайное число от 1 до 10 для param
    get_num = random.randint(1, 10)
    get_response = requests.get(
        f'http://localhost:5001/number/?param={get_num}'
    )
    get_data = get_response.json()  # Парсим JSON-ответ

    # Выполнение POST-запроса
    # Cлучайное число для jsonParam
    post_num = random.randint(1, 10)
    post_response = requests.post(
        'http://localhost:5001/number/',
        json={'jsonParam': post_num},  # Тело запроса в формате JSON
        headers={'Content-Type': 'application/json'}  # Указываем тип контента
    )
    post_data = post_response.json()  # Парсим JSON-ответ

    # Выполнение DELETE-запроса
    del_response = requests.delete('http://localhost:5001/number/')
    del_data = del_response.json()  # Парсим JSON-ответ

    # Формирование математического выражения
    expression_parts = [
        str(get_data['number']),  # Число из GET-запроса
        post_data['operation'],  # Операция из POST-запроса
        str(post_data['number']),  # Число из POST-запроса
        del_data['operation'],  # Операция из DELETE-запроса
        str(del_data['number'])  # Число из DELETE-запроса
    ]
    expression = ' '.join(expression_parts)  # Собираем выражение в строку

    try:
        # Вычисление результата, выполняя строковое выражение как код
        result = eval(expression)
        # Преобразование к целому числу, проверяя деление на ноль
        final_result = int(result) if result != float('inf') else 'Бесконечность'
    except (SyntaxError, TypeError, ZeroDivisionError):
        # Обрабатываем возможные ошибки вычисления
        result = 'error'
        final_result = 'error'

    # Вывод результатов в консоль
    print("\nРезультаты запросов:")
    print(f"1. GET: {get_data['number']} (param={get_num})")
    print(f"2. POST: {post_data['number']} "
          f"(jsonParam={post_num}, operation={post_data['operation']})")
    print(f"3. DELETE: {del_data['number']} "
          f"(operation={del_data['operation']})")
    print(f"\nСоставленное выражение: {expression}")
    print(f"Результат вычисления: {result}")
    print(f"Целочисленный результат: {final_result}")


# Запускаем функцию при выполнении файла
if __name__ == '__main__':
    perform_operations()