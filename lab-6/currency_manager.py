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


def get_db_connection():
    """Устанавливает и возвращает соединение с базой данных.

    Returns:
        connection: Объект соединения с PostgreSQL
    Raises:
        RuntimeError: Если подключение не удалось
    """
    try:
        return psycopg2.connect(**DB_CONFIG)
    except psycopg2.Error as e:
        raise RuntimeError(f"Database connection failed: {e}")


@app.route('/load', methods=['POST'])
def load_currency():
    """Эндпоинт для добавления новой валюты.

    Ожидает JSON в теле запроса:
    {
        "currency_name": "название валюты",
        "rate": курс к рублю
    }

    Returns:
        JSON ответ с статусом операции:
        - 200 OK при успешном добавлении
        - 400 если валюта уже существует
        - 500 при ошибке сервера
    """
    try:
        # Получаем данные из запроса
        data = request.get_json()
        currency_name = data.get('currency_name')
        rate = data.get('rate')

        # Валидация входных данных
        if not currency_name or not rate:
            return jsonify({'error': 'Missing required fields'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Проверяем существование валюты
        cursor.execute(
            "SELECT 1 FROM currencies WHERE currency_name = %s",
            (currency_name,)
        )
        if cursor.fetchone():
            return jsonify({'error': 'Currency already exists'}), 400

        # Добавляем новую валюту
        cursor.execute(
            "INSERT INTO currencies (currency_name, rate) VALUES (%s, %s)",
            (currency_name, rate)
        )
        conn.commit()

        return jsonify({'status': 'OK'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/update_currency', methods=['POST'])
def update_currency():
    """Эндпоинт для обновления курса валюты.

    Ожидает JSON в теле запроса:
    {
        "currency_name": "название валюты",
        "rate": новый курс к рублю
    }

    Returns:
        JSON ответ с статусом операции:
        - 200 OK при успешном обновлении
        - 404 если валюта не найдена
        - 500 при ошибке сервера
    """
    try:
        data = request.get_json()
        currency_name = data.get('currency_name')
        new_rate = data.get('rate')

        # Валидация входных данных
        if not currency_name or not new_rate:
            return jsonify({'error': 'Missing required fields'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Проверяем существование валюты
        cursor.execute(
            "SELECT 1 FROM currencies WHERE currency_name = %s",
            (currency_name,)
        )
        if not cursor.fetchone():
            return jsonify({'error': 'Currency not found'}), 404

        # Обновляем курс
        cursor.execute(
            "UPDATE currencies SET rate = %s WHERE currency_name = %s",
            (new_rate, currency_name)
        )
        conn.commit()

        return jsonify({'status': 'OK'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/delete', methods=['POST'])
def delete_currency():
    """Эндпоинт для удаления валюты.

    Ожидает JSON в теле запроса:
    {
        "currency_name": "название валюты"
    }

    Returns:
        JSON ответ с статусом операции:
        - 200 OK при успешном удалении
        - 404 если валюта не найдена
        - 500 при ошибке сервера
    """
    try:
        data = request.get_json()
        currency_name = data.get('currency_name')

        # Валидация входных данных
        if not currency_name:
            return jsonify({'error': 'Currency name is required'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Проверяем существование валюты
        cursor.execute(
            "SELECT 1 FROM currencies WHERE currency_name = %s",
            (currency_name,)
        )
        if not cursor.fetchone():
            return jsonify({'error': 'Currency not found'}), 404

        # Удаляем валюту
        cursor.execute(
            "DELETE FROM currencies WHERE currency_name = %s",
            (currency_name,)
        )
        conn.commit()

        return jsonify({'status': 'OK'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


# Эндпоинт для получения валюты по названию
@app.route("/currencies/<currency_name>", methods=["GET"])
def get_currency(currency_name):
    conn = get_db_connection()  # Устанавливаем соединение с БД
    cur = conn.cursor()  # Создаём курсор для выполнения SQL-запросов
    cur.execute(
        "SELECT currency_name, rate FROM currencies WHERE currency_name = %s",
        (currency_name,)
    )
    row = cur.fetchone()  # Получаем одну строку результата
    conn.close()  # Закрываем соединение
    if row:
        return jsonify({"currency_name": row[0], "rate": float(row[1])})  # Если валюта найдена
    return jsonify({"error": "Currency not found"}), 404  # Если не найдена — 404


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
    # Запуск приложения на порту 5001
    app.run(port=5001, debug=True)
