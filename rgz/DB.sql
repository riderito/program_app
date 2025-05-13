-- Создание таблицы пользователей
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT UNIQUE NOT NULL,  -- Уникальный идентификатор чата из Telegram
    name VARCHAR(100) NOT NULL,      -- Логин пользователя
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Дата регистрации
);

-- Создание таблицы операций
CREATE TABLE operations (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,              -- Дата операции
    sum DECIMAL(10, 2) NOT NULL,     -- Сумма операции
    chat_id BIGINT NOT NULL,         -- Ссылка на пользователя (идентификатор чата)
    type_operation VARCHAR(10) NOT NULL CHECK (type_operation IN ('ДОХОД', 'РАСХОД')),  -- Тип операции
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Дата создания записи
    FOREIGN KEY (chat_id) REFERENCES users(chat_id) ON DELETE CASCADE
);
