-- Создание таблицы currencies
CREATE TABLE currencies (
    id SERIAL PRIMARY KEY,
    currency_name VARCHAR(50) NOT NULL,
    rate NUMERIC(10, 4) NOT NULL
);

-- Создание таблицы admins
CREATE TABLE admins (
    id SERIAL PRIMARY KEY,
    chat_id VARCHAR(50) NOT NULL
);

INSERT INTO admins VALUES (1, '910380737');
