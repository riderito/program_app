import os # Для доступа к переменным окружения
import logging # Для записи событий (логирования)
from datetime import datetime # Работа с датами и временем
from aiogram import Bot, Dispatcher, types, F # Основные компоненты для бота
from aiogram.filters import Command # Фильтр для обработки команд
from aiogram.fsm.context import FSMContext # Для хранения промежуточных данных
from aiogram.fsm.state import State, StatesGroup # Базовые классы для создания состояний
import psycopg2 # Для работы с PostgreSQL
import httpx # Асинхронный HTTP-клиент для запросов к внешним API

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
        port=5432,
        database="rpp_rgz",
        user="postgres",
        password="postgres"
    )


# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Приветственное сообщение и настройка меню команд"""
    chat_id = message.chat.id

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Проверяем регистрацию пользователя
                cursor.execute("SELECT name FROM users WHERE chat_id = %s", (chat_id,))
                user = cursor.fetchone()

                if user:
                    # Пользователь зарегистрирован
                    username = user[0]
                    welcome_text = (
                        f"👋 Привет, {username}!\n"
                        "Я бот для учета финансов. Вот что я умею:\n\n"
                        "📌 Основные команды:\n"
                        "/start - Показать это меню\n"
                        "/reg - Регистрация (уже выполнена)\n"
                        "/add_operation - Добавить операцию (доход/расход)\n"
                        "/operations - Просмотр операций с сортировкой\n\n"
                        "💡 Просто введите нужную команду или выберите из меню."
                    )
                else:
                    # Пользователь не зарегистрирован
                    welcome_text = (
                        "👋 Привет, незнакомец!\n"
                        "Я бот для учета финансов. Для начала работы нужно зарегистрироваться.\n\n"
                        "📌 Доступные команды:\n"
                        "/reg - Регистрация в системе\n\n"
                        "После регистрации вам станут доступны:\n"
                        "• Добавление операций (/add_operation)\n"
                        "• Просмотр истории операций (/operations)\n\n"
                        "Начните с команды /reg"
                    )

                await message.answer(welcome_text)

        # Формируем список команд для меню
        commands = [
            types.BotCommand(command="start", description="Начало работы"),
            types.BotCommand(command="reg", description="Регистрация"),
            types.BotCommand(command="add_operation", description="Добавить операцию"),
            types.BotCommand(command="operations", description="Просмотр операций с сортировкой")
        ]
        # Определяем, какому именно чату показывать список
        scope = types.BotCommandScopeChat(chat_id=message.chat.id)
        # Определяем, какие команды показывать
        await bot.set_my_commands(commands, scope=scope)

    except Exception as e:
        logger.error(f"Ошибка при обработке /start: {e}")
        await message.answer("⚠️ Произошла ошибка. Попробуйте позже.")


# Создаем состояния (этапы) для регистрации
class RegistrationStates(StatesGroup):
    waiting_for_name = State()  # Состояние ожидания ввода логина


# Обработчик команды /reg - начинает процесс регистрации
@dp.message(Command("reg"))
async def cmd_reg(message: types.Message, state: FSMContext):
    # Извлекаем id чата, с которого пришло сообщение
    chat_id = message.chat.id

    try:
        # Проверяем, зарегистрирован ли уже пользователь
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE chat_id = %s", (chat_id,))
                if cursor.fetchone() is not None:
                    await message.answer("❌ Вы уже зарегистрированы!")
                    return

        # Если не зарегистрирован - просим ввести логин
        await message.answer("📝 Введите ваш логин для регистрации:")
        # Устанавливаем состояние ожидания ввода логина
        await state.set_state(RegistrationStates.waiting_for_name)

    except Exception as e:
        logger.error(f"Ошибка при проверке регистрации: {e}")
        await message.answer("⚠️ Произошла ошибка. Попробуйте позже.")


# Обработчик ввода логина (срабатывает после команды /reg)
@dp.message(RegistrationStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    name = message.text.strip()  # Удаляем лишние пробелы

    # Проверяем, что логин не пустой
    if not name:
        await message.answer("❌ Логин не может быть пустым. Попробуйте еще раз:")
        return

    # Проверяем длину логина
    if len(name) > 100:
        await message.answer("❌ Логин слишком длинный (максимум 100 символов). Введите снова:")
        return

    try:
        # Сохраняем пользователя в базу данных
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (chat_id, name) VALUES (%s, %s)",
                    (chat_id, name)
                )
                conn.commit() # Фиксируем изменения

        # Отправляем сообщение об успешной регистрации
        await message.answer(f"✅ Регистрация успешна, {name}!\n"
                             "Теперь вы можете добавлять операции - /add_operation")

        # Сбрасываем состояние
        await state.clear()

    # Возникает при нарушении ограничений БД
    except psycopg2.IntegrityError:
        await message.answer("❌ Этот логин уже занят. Пожалуйста, выберите другой:")
    except Exception as e:
        logger.error(f"Ошибка при регистрации пользователя: {e}")
        await message.answer("⚠️ Произошла ошибка при регистрации. Попробуйте позже.")
        await state.clear()


# Создаем состояния для добавления операции
class AddOperationStates(StatesGroup):
    waiting_for_type = State()  # Ожидание выбора типа операции
    waiting_for_amount = State()  # Ожидание ввода суммы
    waiting_for_date = State()  # Ожидание ввода даты


# Обработчик команды /add_operation - процесс добавления операции
@dp.message(Command("add_operation"))
async def cmd_add_operation(message: types.Message, state: FSMContext):
    chat_id = message.chat.id

    try:
        # Проверяем, зарегистрирован ли пользователь
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE chat_id = %s", (chat_id,))
                if cursor.fetchone() is None:
                    await message.answer("❌ Вы не зарегистрированы! Сначала выполните /reg")
                    return

        # Создаем клавиатуру с типами операций
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="ДОХОД")],
                [types.KeyboardButton(text="РАСХОД")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )

        await message.answer("📊 Выберите тип операции:", reply_markup=keyboard)
        await state.set_state(AddOperationStates.waiting_for_type)

    except Exception as e:
        logger.error(f"Ошибка при старте добавления операции: {e}")
        await message.answer("⚠️ Произошла ошибка. Попробуйте позже.")


# Обработчик выбора типа операции
@dp.message(AddOperationStates.waiting_for_type, F.text.in_(["ДОХОД", "РАСХОД"]))
async def process_operation_type(message: types.Message, state: FSMContext):
    await state.update_data(type_operation=message.text)  # Сохраняем тип операции
    await message.answer("💵 Введите сумму операции в рублях:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddOperationStates.waiting_for_amount)


# Обработчик некорректного ввода типа операции
@dp.message(AddOperationStates.waiting_for_type)
async def wrong_operation_type(message: types.Message):
    await message.answer("❌ Пожалуйста, выберите тип операции кнопкой:")


# Обработчик ввода суммы операции
@dp.message(AddOperationStates.waiting_for_amount)
async def process_operation_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(',', '.'))  # Поддержка и запятых, и точек
        if amount <= 0:
            await message.answer("❌ Сумма должна быть больше нуля. Введите снова:")
            return

        await state.update_data(sum=amount)  # Сохраняем сумму
        await message.answer("📅 Введите дату операции в формате ДД.ММ.ГГГГ (например, 01.01.2025):")
        await state.set_state(AddOperationStates.waiting_for_date)

    except ValueError:
        await message.answer("❌ Неверный формат суммы. Введите число:")


# Обработчик ввода даты операции и сохранения всей операции
@dp.message(AddOperationStates.waiting_for_date)
async def process_operation_date(message: types.Message, state: FSMContext):
    try:
        # Парсинг строки в дату без времени
        date = datetime.strptime(message.text, "%d.%m.%Y").date()

        # Получаем все сохраненные данные
        data = await state.get_data()
        chat_id = message.chat.id

        # Сохраняем операцию в БД
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO operations (date, sum, chat_id, type_operation) VALUES (%s, %s, %s, %s)",
                    (date, data['sum'], chat_id, data['type_operation'])
                )
                conn.commit()

        await message.answer(f"✅ Операция успешно добавлена!\n"
                             f"Тип: {data['type_operation']}\n"
                             f"Сумма: {round(data['sum'], 2)} руб.\n"
                             f"Дата: {date.strftime('%d.%m.%Y')}")
        await state.clear()

    except ValueError:
        await message.answer("❌ Неверный формат даты. Введите в формате ДД.ММ.ГГГГ:")


# Создаем состояния для просмотра операций
class OperationsStates(StatesGroup):
    waiting_for_sort_column = State()  # Ожидание выбора колонки для сортировки
    waiting_for_sort_direction = State()  # Ожидание выбора направления сортировки
    waiting_for_currency = State()  # Ожидание выбора валюты


# URL для внешнего сервиса курсов валют
EXCHANGE_SERVICE_URL = "http://127.0.0.1:5000/rate"


# При обращении получаем курс валюты от внешнего сервиса
async def get_exchange_rate(currency: str) -> float:
    try:
        # Создаётся асинхронный HTTP-клиент
        async with httpx.AsyncClient() as client:
            response = await client.get(
                EXCHANGE_SERVICE_URL, # URL сервиса курсов валют
                params={"currency": currency}, # Параметры запроса
                timeout=5.0 # Максимальное время ожидания ответа
            )

            if response.status_code == 200:
                return response.json()["rate"]
            elif response.status_code == 400:
                raise ValueError("Неизвестная валюта")
            else:
                raise ValueError("Ошибка сервиса курсов")

    except Exception as e:
        logger.error(f"Ошибка при получении курса: {e}")
        raise


# Обработчик команды /operations - процесс просмотра операций
@dp.message(Command("operations"))
async def cmd_operations(message: types.Message, state: FSMContext):
    chat_id = message.chat.id

    try:
        # Проверяем регистрацию пользователя
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE chat_id = %s", (chat_id,))
                if cursor.fetchone() is None:
                    await message.answer("❌ Вы не зарегистрированы! Сначала выполните /reg")
                    return

        # Клавиатура для выбора колонки сортировки
        columns_keyboard = types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="ДАТА")],
                [types.KeyboardButton(text="СУММА")],
                [types.KeyboardButton(text="ТИП ОПЕРАЦИИ")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )

        await message.answer("📊 Выберите колонку для сортировки:", reply_markup=columns_keyboard)
        await state.set_state(OperationsStates.waiting_for_sort_column)

    except Exception as e:
        logger.error(f"Ошибка при старте просмотра операций: {e}")
        await message.answer("⚠️ Произошла ошибка. Попробуйте позже.")


# Обработчик выбора колонки для сортировки
@dp.message(
    OperationsStates.waiting_for_sort_column,
    F.text.in_(["ДАТА", "СУММА", "ТИП ОПЕРАЦИИ"])
)
async def process_sort_column(message: types.Message, state: FSMContext):
    # Словарь для обработки текста кнопки в название соответствующей колонки
    column_mapping = {
        "ДАТА": "date",
        "СУММА": "sum",
        "ТИП ОПЕРАЦИИ": "type_operation"
    }

    await state.update_data(sort_column=column_mapping[message.text])

    # Клавиатура для выбора направления сортировки
    direction_keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="ПО УБЫВАНИЮ")],
            [types.KeyboardButton(text="ПО ВОЗРАСТАНИЮ")]
        ],
        resize_keyboard=True,
        # Cкрывает клавиатуру бота после её использования
        one_time_keyboard=True
    )

    await message.answer(
        "🔻 Выберите направление сортировки:",
        reply_markup=direction_keyboard
    )
    await state.set_state(OperationsStates.waiting_for_sort_direction)


# Обработчик некорректного выбора колонки
@dp.message(OperationsStates.waiting_for_sort_column)
async def wrong_sort_column(message: types.Message):
    await message.answer("❌ Пожалуйста, выберите колонку для сортировки кнопкой:")


# Обработчик выбора направления сортировки
@dp.message(
    OperationsStates.waiting_for_sort_direction,
    F.text.in_(["ПО УБЫВАНИЮ", "ПО ВОЗРАСТАНИЮ"])
)
async def process_sort_direction(message: types.Message, state: FSMContext):
    # Сохраняем направление сортировки
    sort_direction = "DESC" if message.text == "ПО УБЫВАНИЮ" else "ASC"
    await state.update_data(sort_direction=sort_direction)

    # Клавиатура для выбора валюты
    currency_keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="RUB")],
            [types.KeyboardButton(text="EUR")],
            [types.KeyboardButton(text="USD")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer(
        "💱 Выберите валюту для отображения:",
        reply_markup=currency_keyboard
    )
    await state.set_state(OperationsStates.waiting_for_currency)


# Обработчик некорректного направления сортировки
@dp.message(OperationsStates.waiting_for_sort_direction)
async def wrong_sort_direction(message: types.Message):
    await message.answer("❌ Пожалуйста, выберите направление сортировки кнопкой:")


# Обработчик выбора валюты и вывода операций
@dp.message(OperationsStates.waiting_for_currency, F.text.in_(["RUB", "EUR", "USD"]))
async def process_currency(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    currency = message.text
    data = await state.get_data()

    try:
        # Получаем операции из БД с учетом сортировки
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"SELECT date, sum, type_operation FROM operations "
                    f"WHERE chat_id = %s ORDER BY {data['sort_column']} {data['sort_direction']}",
                    (chat_id,)
                )
                operations = cursor.fetchall()

        if not operations:
            await message.answer(
                "📭 У вас пока нет операций",
                reply_markup=types.ReplyKeyboardRemove() # Явное удаление
            )
            await state.clear()
            return

        # Получаем курс для конвертации
        rate = 1.0  # По умолчанию для RUB
        if currency != "RUB":
            try:
                # Запрашиваем курс у сервиса через функцию
                rate = float(await get_exchange_rate(currency))
            except Exception:
                await message.answer(f"⚠️ Не удалось получить курс {currency}. Показываю в RUB")
                currency = "RUB"

        # Для красивого вывода названий колонок
        column_names = {
            "date": "дате",
            "sum": "сумме",
            "type_operation": "типу операции"
        }

        # Формируем сообщение с операциями
        response = [
            f"📊 Ваши операции (в {currency}), отсортированные по {column_names[data['sort_column']]} "
            f"({'по убыванию' if data['sort_direction'] == 'DESC' else 'по возрастанию'}):\n"
        ]

        # Добавляем сами операции
        for op in operations:
            date, amount, op_type = op
            converted_amount = round(float(amount) / rate, 2)

            response.append(
                f"{date.strftime('%d.%m.%Y')} - "
                f"{converted_amount} {currency} - "
                f"{op_type}"
            )

        await message.answer("\n".join(response), reply_markup=types.ReplyKeyboardRemove())
        await state.clear()

    except Exception as e:
        logger.error(f"Ошибка при получении операций: {e}")
        await message.answer("⚠️ Произошла ошибка при загрузке операций")
        await state.clear()


# Обработчик некорректной валюты
@dp.message(OperationsStates.waiting_for_currency)
async def wrong_currency(message: types.Message):
    await message.answer("❌ Пожалуйста, выберите валюту кнопкой:")


# Основная асинхронная функция для запуска бота
async def main():
    # Запускаем бесконечный цикл опроса серверов на новые сообщения
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    # Запускаем асинхронную функцию main()
    asyncio.run(main())
