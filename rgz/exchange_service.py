from flask import Flask, jsonify, request

app = Flask(__name__)

# Статические курсы валют
EXCHANGE_RATES = {
    "USD": 80.89,  # 1 USD = 80.89 RUB
    "EUR": 90.11  # 1 EUR = 90.11 RUB
}


# Обработчик запроса курса валюты
@app.route('/rate', methods=['GET'])
def get_rate():
    # Получаем переданный в запросе параметр
    currency = request.args.get('currency')

    # Проверяем, передан ли параметр
    if not currency:
        return jsonify({"message": "MISSING CURRENCY PARAMETER"}), 400

    # Приведение к верхнему регистру
    currency = currency.upper()

    try:
        # Если указан некорректный currency, которого нет в словаре
        if currency not in EXCHANGE_RATES:
            return jsonify({"message": "UNKNOWN CURRENCY"}), 400

        # Возвращаем 200 статус со значением курса в теле
        return jsonify({"rate": EXCHANGE_RATES[currency]}), 200

    except Exception as e:
        app.logger.error(f"Ошибка при обработке запроса: {e}")
        # Если ошибка на стороне сервиса
        return jsonify({"message": "UNEXPECTED ERROR"}), 500


if __name__ == '__main__':
    # Режим отладки для удобства
    app.run(debug=True)
