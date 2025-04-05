import requests
import random


def perform_operations():
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

    # Формируем выражение
    expression_parts = [
        str(get_data['number']),
        post_data['operation'],
        str(post_data['number']),
        del_data['operation'],
        str(del_data['number'])
    ]
    expression = ' '.join(expression_parts)

    # Вычисляем результат
    try:
        result = eval(expression)
        final_result = int(result)
    except:
        result = 'calculation error'
        final_result = 'error'

    # Вывод результатов
    print("\nРезультаты запросов:")
    print(f"1. GET: {get_data['number']} (param={get_num}, operation={get_data['operation']})")
    print(f"2. POST: {post_data['number']} (input={post_num}, operation={post_data['operation']})")
    print(f"3. DELETE: {del_data['number']} (operation={del_data['operation']})")
    print(f"\nСоставленное выражение: {expression}")
    print(f"Результат вычисления: {result}")
    print(f"Целочисленный результат: {final_result}")

    return {
        'get_data': get_data,
        'post_data': post_data,
        'del_data': del_data,
        'expression': expression,
        'result': result,
        'final_result': final_result
    }


if __name__ == '__main__':
    perform_operations()