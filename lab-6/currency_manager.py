from flask import Flask, request, jsonify
import psycopg2

# Инициализация Flask приложения
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


# Эндпоинт для добавления новой валюты
@app.route('/load', methods=['POST'])
def load_currency():
    conn = None  # Явно инициализируем переменную
    try:
        # Получаем данные из запроса (название и курс к рублю)
        data = request.get_json()
        currency_name = data.get('currency_name')
        rate = data.get('rate')

        conn = None  # Явно инициализируем переменную

        # Валидация входных данных
        if not currency_name or not rate:
            return jsonify({'error': 'Отсутствуют обязательные поля'}), 400

        conn = get_db_connection()  # Устанавливаем соединение с БД
        cur = conn.cursor()  # Создаём курсор для выполнения SQL-запросов

        # Проверяем существование валюты
        cur.execute(
            "SELECT 1 FROM currencies WHERE currency_name = %s",
            (currency_name,)
        )
        if cur.fetchone():
            return jsonify({'error': 'Валюта уже существует'}), 400

        # Добавляем новую валюту
        cur.execute(
            "INSERT INTO currencies (currency_name, rate) VALUES (%s, %s)",
            (currency_name, rate)
        )
        conn.commit()

        return jsonify({'status': 'OK'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn is not None:  # Проверяем, было ли создано соединение
            conn.close()


# Эндпоинт для обновления курса валюты
@app.route('/update_currency', methods=['POST'])
def update_currency():
    conn = None
    try:
        # Получаем данные из запроса (название и курс к рублю)
        data = request.get_json()
        currency_name = data.get('currency_name')
        new_rate = data.get('rate')

        # Валидация входных данных
        if not currency_name or not new_rate:
            return jsonify({'error': 'Отсутствуют обязательные поля'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Проверяем существование валюты
        cur.execute(
            "SELECT 1 FROM currencies WHERE currency_name = %s",
            (currency_name,)
        )
        if not cur.fetchone():
            return jsonify({'error': 'Валюта не найдена'}), 404

        # Обновляем курс
        cur.execute(
            "UPDATE currencies SET rate = %s WHERE currency_name = %s",
            (new_rate, currency_name)
        )
        conn.commit()

        return jsonify({'status': 'OK'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn is not None:  # Проверяем, было ли создано соединение
            conn.close()


# Эндпоинт для удаления валюты
@app.route('/delete', methods=['POST'])
def delete_currency():
    conn = None
    try:
        # Ожидает JSON в теле запроса с названием валюты
        data = request.get_json()
        currency_name = data.get('currency_name')

        # Валидация входных данных
        if not currency_name:
            return jsonify({'error': 'Требуется указать название валюты'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Проверяем существование валюты
        cur.execute(
            "SELECT 1 FROM currencies WHERE currency_name = %s",
            (currency_name,)
        )
        if not cur.fetchone():
            return jsonify({'error': 'Валюта не найдена'}), 404

        # Удаляем валюту
        cur.execute(
            "DELETE FROM currencies WHERE currency_name = %s",
            (currency_name,)
        )
        conn.commit()

        return jsonify({'status': 'OK'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn is not None:  # Проверяем, было ли создано соединение
            conn.close()


# Эндпоинт для получения валюты по названию
@app.route("/currencies/<currency_name>", methods=["GET"])
def get_currency(currency_name):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT currency_name, rate FROM currencies WHERE currency_name = %s",
        (currency_name,)
    )
    row = cur.fetchone()  # Получаем одну строку результата
    conn.close()  # Закрываем соединение
    if row:
        return jsonify({"currency_name": row[0], "rate": float(row[1])})  # Если валюта найдена
    return jsonify({"error": "Валюта не найдена"}), 404  # Если не найдена - 404


# Эндпоинт для проверки, является ли пользователь администратором
@app.route("/is_admin/<chat_id>", methods=["GET"])
def check_admin(chat_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM admins WHERE chat_id = %s", (chat_id,))

    is_admin = cur.fetchone() is not None  # True, если админ найден
    conn.close()
    return jsonify({"is_admin": is_admin})


if __name__ == '__main__':
    # Запуск сервер на порту 5001
    app.run(port=5001, debug=True)
