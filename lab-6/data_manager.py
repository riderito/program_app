from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# Конфигурация подключения к PostgreSQL
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'rpp',
    'user': 'postgres',
    'password': 'postgres'
}


def get_db_connection():
    """Устанавливает соединение с базой данных"""
    try:
        return psycopg2.connect(**DB_CONFIG)
    except psycopg2.Error as e:
        raise RuntimeError(f"Database connection failed: {e}")


@app.route('/convert', methods=['GET'])
def convert_currency():
    """Эндпоинт для конвертации валюты

    Параметры запроса:
    - currency_name: название валюты (обязательный)
    - amount: сумма для конвертации (обязательный)

    Возвращает:
    - JSON с конвертированной суммой или сообщением об ошибке
    """
    try:
        # Получаем и валидируем параметры
        currency_name = request.args.get('currency_name')
        amount_str = request.args.get('amount')

        if not currency_name or not amount_str:
            return jsonify({'error': 'Missing required parameters: currency_name and amount'}), 400

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            return jsonify({'error': 'Amount must be a positive number'}), 400

        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                # Получаем курс валюты
                cur.execute(
                    "SELECT rate FROM currencies WHERE currency_name = %s",
                    (currency_name.upper(),)
                )
                row = cur.fetchone()

                if not row:
                    return jsonify({'error': 'Currency not found'}), 404

                rate = float(row[0])
                converted_amount = amount * rate

                return jsonify({
                    'original_amount': amount,
                    'currency': currency_name.upper(),
                    'converted_amount': converted_amount,
                    'rate': rate
                }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            if conn:
                conn.close()

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/currencies', methods=['GET'])
def get_all_currencies():
    """Эндпоинт для получения списка всех валют

    Возвращает:
    - JSON-массив всех валют с их курсами
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT currency_name, rate FROM currencies ORDER BY currency_name")
            currencies = [
                {'currency_name': row[0], 'rate': float(row[1])}
                for row in cur.fetchall()
            ]
            return jsonify(currencies), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    app.run(port=5002, debug=True)
