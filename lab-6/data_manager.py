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


# Устанавливает и возвращает соединение с базой данных
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


# Эндпоинт для конвертации валюты
@app.route('/convert', methods=['GET'])
def convert_currency():
    try:
        # Получаем и валидируем параметры
        currency_name = request.args.get('currency_name')
        amount_str = request.args.get('amount')

        if not currency_name or not amount_str:
            return jsonify({'error': 'Отсутствуют обязательные параметры'}), 400

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            return jsonify({'error': 'Сумма должна быть положительным числом'}), 400

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
                    return jsonify({'error': 'Валюта не найдена'}), 404

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
            if conn is not None:  # Проверяем, было ли создано соединение
                conn.close()

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Эндпоинт для получения списка всех валют
@app.route('/currencies', methods=['GET'])
def get_all_currencies():
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
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    app.run(port=5002, debug=True)
