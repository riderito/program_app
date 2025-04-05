from flask import Flask, request, jsonify
import random

app = Flask(__name__)


@app.route('/number/', methods=['GET', 'POST', 'DELETE'])  # Добавил слеш для единообразия
def handle_number():
    if request.method == 'GET':
        try:
            param = float(request.args.get('param', 1))
            result = random.uniform(1, 100) * param
            return jsonify({
                'status': 'success',
                'number': round(result, 2),
                'operation': '*',
                'param': param
            })
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Invalid parameter'}), 400

    elif request.method == 'POST':
        if not request.is_json:
            return jsonify({'status': 'error', 'message': 'Request must be JSON'}), 400

        data = request.get_json()
        try:
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
                'status': 'success',
                'number': round(result, 2),
                'operation': operation,
                'input_number': num
            })
        except (TypeError, ValueError):
            return jsonify({'status': 'error', 'message': 'Invalid jsonParam'}), 400

    elif request.method == 'DELETE':
        return jsonify({
            'status': 'success',
            'number': round(random.uniform(1, 100), 2),
            'operation': random.choice(['+', '-', '*', '/'])
        })


if __name__ == '__main__':
    app.run(port=5001, debug=True)