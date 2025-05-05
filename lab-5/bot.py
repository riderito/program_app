import os  # Для доступа к переменным окружения
import logging  # Для записи событий (логирования)
from aiogram import Bot, Dispatcher, types, F # Основные компоненты для бота
from aiogram.filters import Command # Для обработки команд
from aiogram.fsm.context import FSMContext # Для хранения промежуточных данных
from aiogram.fsm.state import State, StatesGroup # Состояния FSM
from aiogram.utils.keyboard import ReplyKeyboardBuilder # Для создания клавиатур
import psycopg2 # Для работы с PostgreSQL

# Настройка логирования: выводится информация в консоль
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем токен бота из переменной окружения
API_TOKEN = os.getenv("API_TOKEN")

# Создаём экземпляр бота
bot = Bot(token=API_TOKEN)
# Создаём диспетчер (обработчик команд)
dp = Dispatcher()

# Функция для подключения к базе данных
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        port = 5432,
        database="rpp",
        user="postgres",
        password="postgres"
    )


# Класс состояний FSM для управления валютами
class CurrencyStates(StatesGroup):
    waiting_for_currency_name = State()
    waiting_for_currency_rate = State()
    waiting_for_currency_to_delete = State()
    waiting_for_currency_to_update = State()
    waiting_for_currency_rate_to_update = State()
    waiting_for_currency_to_convert = State()
    waiting_for_amount_to_convert = State()


# Функция проверки прав администратора
async def is_admin(chat_id) -> bool:
    try:
        # Устанавливаем соединение с БД
        with get_db_connection() as conn:
            # Создаем курсор
            with conn.cursor() as cur:
                # Проверяем наличие id пользователя в таблице admins
                cur.execute("SELECT id FROM admins WHERE chat_id = %s",
                            (str(chat_id),))
                # Возвращаем True если пользователь найден
                return cur.fetchone() is not None
    except Exception as e:
        logger.error(f"Ошибка при проверке администратора: {e}") # Логируем ошибку
        return False


# Обработчик команды /start
@dp.message(Command("start"))
async def start(message: types.Message):
    # Формируем список команд в зависимости от прав пользователя
    # Для администратора
    if await is_admin(message.chat.id):
        commands = [
            types.BotCommand(command="start", description="Начало работы"),
            types.BotCommand(command="manage_currency", description="Управление валютами"),
            types.BotCommand(command="get_currencies", description="Список всех валют"),
            types.BotCommand(command="convert", description="Конвертация валюты"),
            types.BotCommand(command="help", description="Доступные команды")
        ]
    # Для обычных пользователей
    else:
        commands = [
            types.BotCommand(command="start", description="Начало работы"),
            types.BotCommand(command="get_currencies", description="Список всех валют"),
            types.BotCommand(command="convert", description="Конвертация валюты"),
            types.BotCommand(command="help", description="Доступные команды")
        ]

    # Определяем, какому именно чату показывать список
    scope = types.BotCommandScopeChat(chat_id=message.chat.id)
    # Определяем, какие команды показывать
    await bot.set_my_commands(commands, scope=scope)

    await message.answer("Привет!🤗\n"
                         "Обратись к 'Меню' или используй "
                         "/help для просмотра доступных команд")


# Обработчик команды /help
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    # Формируем список доступных команд в зависимости от прав
    if await is_admin(message.chat.id):
        text = (
            "Доступные команды:\n"
            "/start - Начало работы\n"
            "/manage_currency - Управление валютами\n"
            "/get_currencies - Список всех валют\n"
            "/convert - Конвертация валюты"
        )
    else:
        text = (
            "Доступные команды:\n"
            "/start - Начало работы\n"
            "/get_currencies - Список всех валют\n"
            "/convert - Конвертация валюты"
        )
    await message.answer(text)


# Обработчик команды управления валютами (только для админов)
@dp.message(Command("manage_currency"))
async def manage_currency(message: types.Message):
    if not await is_admin(message.chat.id):
        await message.answer("Нет доступа к команде")
        return

    # Создаем клавиатуру с действиями для администратора
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text="Добавить валюту"),
        types.KeyboardButton(text="Удалить валюту"),
        types.KeyboardButton(text="Изменить курс валюты")
    )
    builder.adjust(3)  # Располагаем 3 кнопки в один ряд

    await message.answer(
        "Выберите действие:",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )


# Обработчик кнопки "Добавить валюту"
@dp.message(F.text == "Добавить валюту")
async def add_currency_start(message: types.Message, state: FSMContext):
    if not await is_admin(message.chat.id):
        await message.answer("Нет доступа к команде")
        return
    await message.answer("Введите название валюты:")
    await state.set_state(CurrencyStates.waiting_for_currency_name)


# Обработчик ввода названия валюты для добавления
@dp.message(CurrencyStates.waiting_for_currency_name)
async def add_currency_name(message: types.Message, state: FSMContext):
    # Приводим к верхнему регистру и убираем пробелы
    currency_name = message.text.upper().strip()

    # Валидация ввода: только буквы, длина от 2 до 5
    if not currency_name.isalpha() or not (2 <= len(currency_name) <= 5):
        await message.answer(
            "⛔ Название валюты должно содержать только буквы (от 2 до 5 символов)."
        )
        return

    # Проверка существования валюты
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id FROM currencies WHERE currency_name = %s",
                    (currency_name,)
                )
                if cur.fetchone() is not None:
                    await message.answer("Данная валюта уже существует")
                    await state.clear()
                    return

        # Сохраняем название валюты в состоянии
        await state.update_data(currency_name=currency_name)
        await message.answer("Введите курс к рублю:")
        await state.set_state(CurrencyStates.waiting_for_currency_rate)

    except Exception as e:
        logger.error(f"Ошибка при проверке валюты: {e}")
        await message.answer("Произошла ошибка, попробуйте позже")
        await state.clear()


# Обработчик ввода курса валюты для добавления
@dp.message(CurrencyStates.waiting_for_currency_rate)
async def add_currency_rate(message: types.Message, state: FSMContext):
    try:
        # Преобразуем ввод в число и заменяем запятую на точку
        rate = float(message.text.replace(",", "."))
        # Проверка на положительное значение
        if rate <= 0:
            raise ValueError

        data = await state.get_data()
        currency_name = data['currency_name']

        # Сохраняем валюту в базу данных
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO currencies (currency_name, rate) "
                    "VALUES (%s, %s)",(currency_name, rate)
                )
                conn.commit() # Фиксируем изменения

        await message.answer(
            f"Валюта {currency_name} успешно добавлена",
            reply_markup=types.ReplyKeyboardRemove() # Убираем клавиатуру
        )
        await state.clear() # Сбрасываем состояние

    except ValueError:
        await message.answer("Пожалуйста, введите корректное число (больше 0):")
    except Exception as e:
        logger.error(f"Ошибка при добавлении валюты: {e}")
        await message.answer("Произошла ошибка, попробуйте позже")
        await state.clear()


# Обработчик кнопки "Удалить валюту"
@dp.message(F.text == "Удалить валюту")
async def delete_currency_start(message: types.Message, state: FSMContext):
    if not await is_admin(message.chat.id):
        await message.answer("Нет доступа к команде")
        return
    await message.answer("Введите название валюты для удаления:")
    await state.set_state(CurrencyStates.waiting_for_currency_to_delete)


# Обработчик ввода названия валюты для удаления
@dp.message(CurrencyStates.waiting_for_currency_to_delete)
async def delete_currency(message: types.Message, state: FSMContext):
    currency_name = message.text.upper().strip()

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Удаляем валюту из БД
                cur.execute(
                    "DELETE FROM currencies WHERE currency_name = %s",
                    (currency_name,)
                )
                deleted_rows = cur.rowcount # Получаем количество удаленных строк
                conn.commit()

        if deleted_rows > 0:
            await message.answer(
                f"Валюта {currency_name} успешно удалена",
                reply_markup=types.ReplyKeyboardRemove()
            )
        else:
            await message.answer(
                "Валюта не найдена",
                reply_markup=types.ReplyKeyboardRemove()
            )

    except Exception as e:
        logger.error(f"Ошибка при удалении валюты: {e}")
        await message.answer("Произошла ошибка, попробуйте позже")
    finally:
        await state.clear()


# Обработчик кнопки "Изменить курс валюты"
@dp.message(F.text == "Изменить курс валюты")
async def update_currency_start(message: types.Message, state: FSMContext):
    if not await is_admin(message.chat.id):
        await message.answer("Нет доступа к команде")
        return
    await message.answer("Введите название валюты:")
    await state.set_state(CurrencyStates.waiting_for_currency_to_update)


# Обработчик ввода названия валюты для изменения
@dp.message(CurrencyStates.waiting_for_currency_to_update)
async def update_currency_name(message: types.Message, state: FSMContext):
    currency_name = message.text.upper().strip()

    # Проверка существования валюты в БД
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id FROM currencies WHERE currency_name = %s",
                    (currency_name,)
                )
                if cur.fetchone() is None:
                    await message.answer("Валюта не найдена")
                    await state.clear()
                    return

        await state.update_data(currency_name=currency_name)
        await message.answer("Введите новый курс к рублю:")
        await state.set_state(CurrencyStates.waiting_for_currency_rate_to_update)

    except Exception as e:
        logger.error(f"Ошибка при проверке валюты: {e}")
        await message.answer("Произошла ошибка, попробуйте позже")
        await state.clear()


# Обработчик ввода нового курса валюты
@dp.message(CurrencyStates.waiting_for_currency_rate_to_update)
async def update_currency_rate(message: types.Message, state: FSMContext):
    try:
        rate = float(message.text.replace(",", "."))
        if rate <= 0:
            raise ValueError

        data = await state.get_data()
        currency_name = data['currency_name']

        # Обновление курса валюты в базе данных
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE currencies SET rate = %s "
                    "WHERE currency_name = %s",(rate, currency_name)
                )
                conn.commit()

        await message.answer(
            f"Курс валюты {currency_name} успешно обновлен",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.clear()

    except ValueError:
        await message.answer("Пожалуйста, введите корректное число (больше 0):")
    except Exception as e:
        logger.error(f"Ошибка при обновлении курса: {e}")
        await message.answer("Произошла ошибка, попробуйте позже")
        await state.clear()


# Обработчик команды получения списка валют
@dp.message(Command("get_currencies"))
async def get_currencies(message: types.Message):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Получаем все существующие в БД валюты
                cur.execute("SELECT currency_name, rate FROM currencies ORDER BY currency_name")
                currencies = cur.fetchall()

        if not currencies:
            await message.answer("Нет доступных валют")
            return

        # Формируем ответ с форматированием
        response = "Список доступных валют:\n\n"
        for currency in currencies:
            response += f"{currency[0]} - {currency[1]:.2f} руб.\n"

        await message.answer(response)

    except Exception as e:
        logger.error(f"Ошибка при получении списка валют: {e}")
        await message.answer("Произошла ошибка при получении списка валют")


# Обработчик команды для конвертации валюты
@dp.message(Command("convert"))
async def convert_start(message: types.Message, state: FSMContext):
    await message.answer("Введите название валюты:")
    await state.set_state(CurrencyStates.waiting_for_currency_to_convert)


# Обработчик ввода названия валюты для конвертации
@dp.message(CurrencyStates.waiting_for_currency_to_convert)
async def convert_currency_name(message: types.Message, state: FSMContext):
    currency_name = message.text.upper().strip()

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Получаем курс валюты из БД
                cur.execute(
                    "SELECT rate FROM currencies WHERE currency_name = %s",
                    (currency_name,)
                )
                result = cur.fetchone()

                if result is None:
                    await message.answer("Валюта не найдена")
                    await state.clear()
                    return

                # Сохраняем данные для конвертации
                await state.update_data({
                    'currency_name': currency_name,
                    'rate': float(result[0])  # Преобразуем numeric в float
                })
                await message.answer("Введите сумму для конвертации:")
                await state.set_state(CurrencyStates.waiting_for_amount_to_convert)

    except Exception as e:
        logger.error(f"Ошибка при конвертации валюты: {e}")
        await message.answer("Произошла ошибка, попробуйте позже")
        await state.clear()


# Обработчик ввода суммы для конвертации
@dp.message(CurrencyStates.waiting_for_amount_to_convert)
async def convert_amount(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()

        amount = float(message.text.replace(",", "."))
        if amount <= 0:
            raise ValueError

        currency_name = data['currency_name']
        rate = data['rate']
        total = amount * rate # Вычисляем результат конвертации

        await message.answer(
            f"{amount} {currency_name} = {total:.2f} руб."
        )
        await state.clear()

    except ValueError:
        await message.answer("Пожалуйста, введите корректную сумму (больше 0):")
    except Exception as e:
        logger.error(f"Ошибка при конвертации: {e}")
        await message.answer("Произошла ошибка, попробуйте позже")
        await state.clear()


# Основная асинхронная функция для запуска бота
async def main() -> None:
    # Запускаем бесконечный цикл опроса серверов на новые сообщения
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    # Запускаем асинхронную функцию main()
    asyncio.run(main())
