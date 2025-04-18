# Flask для сервера, request для обработки запросов, jsonify для JSON-ответов
from flask import Flask, request, jsonify
# Для генерации случайных чисел
import random

# Создание экземпляра Flask-приложения
app = Flask(__name__)


# GET-эндпоинт для умножения случайного числа на параметр запроса
@app.route('/number/', methods=['GET'])
def get_number():
    """
    Обрабатывает GET-запрос к /number/.
    Принимает параметр 'param' (число) из строки запроса.
    Возвращает JSON с результатом умножения случайного числа на param.
    """
    try:
        # Пытаемся получить параметр 'param' из запроса и преобразовать его в float
        # Если параметр не указан, используем значение по умолчанию 1
        param = float(request.args.get('param', 1))
    except TypeError:
        # Если преобразование не удалось (передали строку), возвращаем ошибку 400
        return jsonify({
            'status': 'error',
            'message': 'Недопустимый параметр'
        }), 400

    # Генерируем случайное число от 1 до 100
    rand_num = random.uniform(1, 100)
    # Вычисляем результат умножения
    result = rand_num * param

    # Возвращаем результат в JSON-формате, округлённый до 2 знаков после запятой
    return jsonify({
        'number': round(result, 2)
    })


# POST-эндпоинт для выполнения случайной операции с числом из JSON-тела запроса
@app.route('/number/', methods=['POST'])
def post_number():
    """
    Обрабатывает POST-запрос к /number/.
    Принимает JSON с полем 'jsonParam' (число) в теле запроса.
    Возвращает JSON с результатом умножения случайного числа на jsonParam и случайной операцией (+,-,*,/)
    """
    # Проверяем, что запрос содержит JSON
    if not request.is_json:
        return jsonify({
            'status': 'error',
            'message': 'Запрос должен быть в формате JSON'
        }), 400

    # Парсим JSON из тела запроса
    data = request.get_json()
    try:
        # Пытаемся получить параметр 'jsonParam' и преобразовать его в float
        # Если параметр не указан, используем значение по умолчанию 1
        num = float(data.get('jsonParam', 1))
    except TypeError:
        # Если преобразование не удалось, возвращаем ошибку 400
        return jsonify({
            'status': 'error',
            'message': 'Недопустимый jsonParam'
        }), 400

    # Генерируем случайное число от 1 до 100
    rand_num = random.uniform(1, 100)
    # Вычисляем результат умножения
    result = rand_num * num

    # Выбираем случайную операцию из списка
    operation = random.choice(['+', '-', '*', '/'])

    # Возвращаем результат и выбранную операцию
    return jsonify({
        'number': round(result, 2),
        'operation': operation
    })


# DELETE-эндпоинт для возврата случайного числа и операции
@app.route('/number/', methods=['DELETE'])
def delete_number():
    """
    Обрабатывает DELETE-запрос к /number/.
    Не принимает параметров.
    Возвращает JSON со случайным числом и случайной операцией.
    """
    return jsonify({
        'number': round(random.uniform(1, 100), 2),  # Случайное число, округлённое до 2 знаков
        'operation': random.choice(['+', '-', '*', '/'])  # Случайная операция
    })


# Запуск сервера при выполнении файла
if __name__ == '__main__':
    app.run(port=5001, debug=True)