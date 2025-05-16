# Импорт Flask и psycopg2
from flask import Flask, request, jsonify
import psycopg2

# Создание Flask-приложения
app = Flask(__name__)

# Конфигурация для подключения к БД
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'rpp',
    'user': 'postgres',
    'password': 'postgres'
}


# Функция подключения к PostgreSQL
def get_db():
    return psycopg2.connect(**DB_CONFIG)


# Эндпоинт для конвертации валюты
@app.route('/convert')
def convert():
    # Получаем параметры из URL: /convert?currency_name=USD&amount=100
    currency_name = request.args.get('currency_name')
    amount = float(request.args.get('amount'))  # Преобразуем в число

    conn = get_db()
    cur = conn.cursor()

    # Ищем курс нужной валюты
    cur.execute(
        "SELECT rate FROM currencies WHERE currency_name = %s",
        (currency_name,)
    )
    row = cur.fetchone()
    if not row:
        return jsonify({'error': 'Currency not found'}), 404  # Ошибка, если нет такой валюты

    rate = row[0]
    return jsonify({'converted': amount * rate}), 200  # Возвращаем результат


# Эндпоинт для получения списка всех валют
@app.route('/currencies')
def get_currencies():
    conn = get_db()
    cur = conn.cursor()

    # Получаем все валюты
    cur.execute("SELECT currency_name, rate FROM currencies")
    # Преобразуем в список словарей
    currencies = [{'currency_name': row[0], 'rate': row[1]} for row in cur.fetchall()]
    return jsonify(currencies), 200


# Эндпоинт для получения одной валюты
@app.route('/currencies/<currency_name>', methods=['GET'])
def get_currency(currency_name):
    conn = get_db()
    cur = conn.cursor()

    # Получаем валюту по имени
    cur.execute(
        "SELECT currency_name, rate FROM currencies WHERE currency_name = %s",
        (currency_name.upper(),)
    )
    row = cur.fetchone()

    if not row:
        return jsonify({'error': 'Currency not found'}), 404

    return jsonify({'currency_name': row[0], 'rate': row[1]}), 200


# Запуск Flask-приложения
if __name__ == '__main__':
    app.run(port=5002)
