# Импорт необходимых модулей из Flask и библиотеки для работы с PostgreSQL
from flask import Flask, request, jsonify  # Flask — микрофреймворк для создания веб-серверов
import psycopg2  # psycopg2 — библиотека для подключения к PostgreSQL

# Создание экземпляра Flask-приложения
app = Flask(__name__)

# Конфигурация подключения к базе данных PostgreSQL
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'rpp',
    'user': 'postgres',
    'password': 'postgres'
}


# Вспомогательная функция для подключения к БД
def get_db():
    return psycopg2.connect(**DB_CONFIG)


# Эндпоинт для получения валюты по названию
@app.route("/currencies/<currency_name>", methods=["GET"])
def get_currency(currency_name):
    conn = get_db()  # Устанавливаем соединение с БД
    cur = conn.cursor()  # Создаём курсор для выполнения SQL-запросов
    cur.execute("SELECT currency_name, rate FROM currencies WHERE currency_name = %s", (currency_name,))
    row = cur.fetchone()  # Получаем одну строку результата
    conn.close()  # Закрываем соединение
    if row:
        return jsonify({"currency_name": row[0], "rate": float(row[1])})  # Если валюта найдена
    return jsonify({"error": "Currency not found"}), 404  # Если не найдена — 404


# Эндпоинт для добавления новой валюты
@app.route("/currencies", methods=["POST"])
def add_currency():
    data = request.json  # Получаем JSON-данные из запроса
    name = data["currency_name"]
    rate = data["rate"]
    conn = get_db()
    cur = conn.cursor()

    # Проверка: есть ли такая валюта уже
    cur.execute("SELECT * FROM currencies WHERE currency_name = %s", (name,))
    if cur.fetchone():
        return jsonify({"error": "Currency already exists"}), 400  # Возвращаем ошибку, если валюта уже есть

    # Вставляем новую валюту
    cur.execute("INSERT INTO currencies (currency_name, rate) VALUES (%s, %s)", (name, rate))
    conn.commit()  # Сохраняем изменения
    conn.close()
    return jsonify({"status": "OK"}), 201  # Возвращаем статус создания (201)


# Эндпоинт для удаления валюты
@app.route("/currencies/<currency_name>", methods=["DELETE"])
def delete_currency(currency_name):
    conn = get_db()
    cur = conn.cursor()

    # Проверка: существует ли валюта
    cur.execute("SELECT * FROM currencies WHERE currency_name = %s", (currency_name,))
    if not cur.fetchone():
        return jsonify({"error": "Currency not found"}), 404  # Если не существует — ошибка

    # Удаление валюты
    cur.execute("DELETE FROM currencies WHERE currency_name = %s", (currency_name,))
    conn.commit()
    conn.close()
    return jsonify({"status": "Deleted"}), 200


# Эндпоинт для обновления курса валюты
@app.route("/currencies/<currency_name>", methods=["PUT"])
def update_currency(currency_name):
    data = request.json  # Получаем JSON-данные
    rate = data["rate"]  # Новый курс

    conn = get_db()
    cur = conn.cursor()

    # Проверка: есть ли валюта
    cur.execute("SELECT * FROM currencies WHERE currency_name = %s", (currency_name,))
    if not cur.fetchone():
        return jsonify({"error": "Currency not found"}), 404

    # Обновление курса
    cur.execute("UPDATE currencies SET rate = %s WHERE currency_name = %s", (rate, currency_name))
    conn.commit()
    conn.close()
    return jsonify({"status": "Updated"}), 200


# Эндпоинт для проверки, является ли пользователь администратором
@app.route("/is_admin/<chat_id>", methods=["GET"])
def check_admin(chat_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM admins WHERE chat_id = %s", (chat_id,))
    is_admin = cur.fetchone() is not None  # True, если админ найден
    conn.close()
    return jsonify({"is_admin": is_admin})


# Запуск Flask-приложения
if __name__ == "__main__":
    app.run(port=5001)

