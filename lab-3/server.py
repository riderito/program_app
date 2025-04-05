from flask import Flask, request, jsonify
import random
import requests
from datetime import datetime

app = Flask(__name__)


# Основные API endpoints
@app.route('/number/', methods=['GET'])
def get_number():
    param = float(request.args.get('param', 1))
    result = random.uniform(1, 100) * param
    return jsonify({
        'number': round(result, 2),
        'operation': '*',
        'param': param,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/number/', methods=['POST'])
def post_number():
    data = request.get_json()
    num = float(data.get('jsonParam', 1))
    rand_num = random.uniform(1, 100)
    operation = random.choice(['+', '-', '*', '/'])

    if operation == '+':
        result = rand_num + num
    elif operation == '-':
        result = rand_num - num
    elif operation == '*':
        result = rand_num * num
    else:
        result = rand_num / num if num != 0 else float('inf')

    return jsonify({
        'number': round(result, 2),
        'operation': operation,
        'input_number': num,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/number/', methods=['DELETE'])
def delete_number():
    return jsonify({
        'number': round(random.uniform(1, 100), 2),
        'operation': random.choice(['+', '-', '*', '/']),
        'timestamp': datetime.now().isoformat()
    })


# Текстовый интерфейс для вывода результатов
@app.route('/')
def text_interface():
    # Выполняем все три запроса
    try:
        # 1. GET запрос
        get_num = random.randint(1, 10)
        get_response = requests.get(f'http://localhost:5001/number/?param={get_num}')
        get_data = get_response.json()

        # 2. POST запрос
        post_num = random.randint(1, 10)
        post_response = requests.post(
            'http://localhost:5001/number/',
            json={'jsonParam': post_num},
            headers={'Content-Type': 'application/json'}
        )
        post_data = post_response.json()

        # 3. DELETE запрос
        del_response = requests.delete('http://localhost:5001/number/')
        del_data = del_response.json()

        # Формируем текстовый отчет
        report = [
            "=== РЕЗУЛЬТАТЫ ВЫЧИСЛЕНИЙ ===",
            f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "[1] GET ЗАПРОС:",
            f"  URL: /number/?param={get_num}",
            f"  Результат: {get_data['number']}",
            f"  Операция: умножение (*)",
            f"  Параметр: {get_data['param']}",
            f"  Время выполнения: {get_data['timestamp']}",
            "",
            "[2] POST ЗАПРОС:",
            f"  URL: /number/",
            f"  Тело запроса: {{'jsonParam': {post_num}}}",
            f"  Результат: {post_data['number']}",
            f"  Операция: {post_data['operation']}",
            f"  Входное число: {post_data['input_number']}",
            f"  Время выполнения: {post_data['timestamp']}",
            "",
            "[3] DELETE ЗАПРОС:",
            f"  URL: /number/",
            f"  Случайное число: {del_data['number']}",
            f"  Случайная операция: {del_data['operation']}",
            f"  Время выполнения: {del_data['timestamp']}",
            "",
            "=== ИТОГОВОЕ ВЫРАЖЕНИЕ ===",
            f"Выражение: {get_data['number']} {post_data['operation']} {post_data['number']} {del_data['operation']} {del_data['number']}"
        ]

        # Вычисляем результат
        try:
            expression = f"{get_data['number']} {post_data['operation']} {post_data['number']} {del_data['operation']} {del_data['number']}"
            result = eval(expression)
            final_result = int(result)
            report.extend([
                f"Результат: {result}",
                f"Целочисленный итог: {final_result}",
                "",
                "СТАТУС: ВЫЧИСЛЕНИЕ УСПЕШНО"
            ])
        except Exception as e:
            report.extend([
                "ОШИБКА ВЫЧИСЛЕНИЯ:",
                str(e),
                "",
                "СТАТУС: ОШИБКА"
            ])

        return "\n".join(report), 200, {'Content-Type': 'text/plain; charset=utf-8'}

    except Exception as e:
        error_msg = f"ОШИБКА: {str(e)}\n\nПопробуйте обновить страницу"
        return error_msg, 500, {'Content-Type': 'text/plain; charset=utf-8'}


if __name__ == '__main__':
    app.run(port=5001, debug=True)