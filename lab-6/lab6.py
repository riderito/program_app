# Импорт необходимых модулей
import os  # Работа с переменными окружения
import logging  # Логирование событий
from aiogram import Bot, Dispatcher, types, F  # Основные компоненты aiogram
from aiogram.filters import Command  # Фильтр для команд
from aiogram.fsm.context import FSMContext  # Контекст для управления состояниями
from aiogram.fsm.state import State, StatesGroup  # Определение состояний FSM
from aiogram.utils.keyboard import ReplyKeyboardBuilder  # Создание клавиатур
import aiohttp  # Асинхронные HTTP-запросы
import asyncio  # Асинхронное программирование

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получение токена бота из переменной окружения
API_TOKEN = os.getenv("API_TOKEN")

# Создание экземпляров бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# URL-адреса микросервисов для управления валютами и получения данных
CURRENCY_MANAGER_URL = "http://127.0.0.1:5001"
DATA_MANAGER_URL = "http://127.0.0.1:5002"

# Определение состояний для управления валютами с использованием FSM
class CurrencyStates(StatesGroup):
    waiting_for_currency_name = State()  # Ожидание ввода названия валюты
    waiting_for_currency_rate = State()  # Ожидание ввода курса валюты
    waiting_for_currency_to_delete = State()  # Ожидание ввода валюты для удаления
    waiting_for_currency_to_update = State()  # Ожидание ввода валюты для обновления
    waiting_for_currency_rate_to_update = State()  # Ожидание ввода нового курса валюты
    waiting_for_currency_to_convert = State()  # Ожидание ввода валюты для конвертации
    waiting_for_amount_to_convert = State()  # Ожидание ввода суммы для конвертации

# Функция для проверки, является ли пользователь администратором
async def is_admin(chat_id: int) -> bool:
    async with aiohttp.ClientSession() as session:
        try:
            # Отправка GET-запроса для проверки статуса администратора
            async with session.get(f"{CURRENCY_MANAGER_URL}/is_admin/{chat_id}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("is_admin", False)
        except Exception as e:
            logger.error(f"Ошибка при проверке администратора: {e}")
    return False

# Обработчик команды /start
@dp.message(Command("start"))
async def start(message: types.Message):
    # Проверка, является ли пользователь администратором
    if await is_admin(message.chat.id):
        # Список команд для администратора
        commands = [
            types.BotCommand(command="start", description="Начало работы"),
            types.BotCommand(command="manage_currency", description="Управление валютами"),
            types.BotCommand(command="get_currencies", description="Список всех валют"),
            types.BotCommand(command="convert", description="Конвертация валюты"),
            types.BotCommand(command="help", description="Доступные команды")
        ]
    else:
        # Список команд для обычного пользователя
        commands = [
            types.BotCommand(command="start", description="Начало работы"),
            types.BotCommand(command="get_currencies", description="Список всех валют"),
            types.BotCommand(command="convert", description="Конвертация валюты"),
            types.BotCommand(command="help", description="Доступные команды")
        ]

    # Установка команд для конкретного чата
    scope = types.BotCommandScopeChat(chat_id=message.chat.id)
    await bot.set_my_commands(commands, scope=scope)

    # Приветственное сообщение
    await message.answer("Привет! 🤗\nОбратись к 'Меню' или используй /help для просмотра доступных команд")

# Обработчик команды /help
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    # Проверка, является ли пользователь администратором
    if await is_admin(message.chat.id):
        # Список доступных команд для администратора
        text = (
            "Доступные команды:\n"
            "/start - Начало работы\n"
            "/manage_currency - Управление валютами\n"
            "/get_currencies - Список всех валют\n"
            "/convert - Конвертация валюты"
        )
    else:
        # Список доступных команд для обычного пользователя
        text = (
            "Доступные команды:\n"
            "/start - Начало работы\n"
            "/get_currencies - Список всех валют\n"
            "/convert - Конвертация валюты"
        )
    # Отправка списка команд
    await message.answer(text)

# Обработчик команды /manage_currency
@dp.message(Command("manage_currency"))
async def manage_currency(message: types.Message):
    # Проверка, является ли пользователь администратором
    if not await is_admin(message.chat.id):
        await message.answer("Нет доступа к команде")
        return

    # Создание клавиатуры с вариантами управления валютами
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text="Добавить валюту"),
        types.KeyboardButton(text="Удалить валюту"),
        types.KeyboardButton(text="Изменить курс валюты")
    )
    builder.adjust(3)  # Установка количества кнопок в строке

    # Отправка сообщения с клавиатурой
    await message.answer(
        "Выберите действие:",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

# Обработчик кнопки "Добавить валюту"
@dp.message(F.text == "Добавить валюту")
async def add_currency_start(message: types.Message, state: FSMContext):
    # Проверка, является ли пользователь администратором
    if not await is_admin(message.chat.id):
        await message.answer("Нет доступа к команде")
        return
    # Запрос ввода названия валюты
    await message.answer("Введите название валюты:")
    # Установка состояния ожидания ввода названия валюты
    await state.set_state(CurrencyStates.waiting_for_currency_name)

# Обработчик ввода названия валюты для добавления
@dp.message(CurrencyStates.waiting_for_currency_name)
async def add_currency_name(message: types.Message, state: FSMContext):
    # Преобразование введенного названия валюты к верхнему регистру и удаление пробелов
    currency_name = message.text.upper().strip()

    # Проверка корректности названия валюты
    if not currency_name.isalpha() or not (2 <= len(currency_name) <= 5):
        await message.answer("⛔ Название валюты должно содержать только буквы (от 2 до 5 символов).")
        return

    # Проверка, существует ли уже такая валюта
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{CURRENCY_MANAGER_URL}/currencies/{currency_name}") as resp:
                if resp.status == 200:
                    await message.answer("Данная валюта уже существует")
                    await state.clear()
                    return
        except Exception as e:
            logger.error(f"Ошибка при проверке валюты: {e}")
            await message.answer("Произошла ошибка, попробуйте позже")
            await state.clear()
            return

    # Сохранение названия валюты в состоянии
    await state.update_data(currency_name=currency_name)
    # Запрос ввода курса валюты
    await message.answer("Введите курс к рублю:")
    # Установка состояния ожидания ввода курса валюты
    await state.set_state(CurrencyStates.waiting_for_currency_rate)

# Обработчик ввода курса валюты для добавления
@dp.message(CurrencyStates.waiting_for_currency_rate)
async def add_currency_rate(message: types.Message, state: FSMContext):
    try:
        # Преобразование введенного значения в число с плавающей точкой
        rate = float(message.text.replace(",", "."))
        if rate <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число (больше 0):")
        return

    # Получение сохраненных данных из состояния
    data = await state.get_data()
    currency_name = data['currency_name']

    # Отправка запроса на добавление новой валюты
    async with aiohttp.ClientSession() as session:
        try:
            payload = {"currency_name": currency_name, "rate": rate}
            async with session.post(f"{CURRENCY_MANAGER_URL}/currencies", json=payload) as resp:
                if resp.status == 201:
                    await message.answer(f"Валюта {currency_name} успешно добавлена", reply_markup=types.ReplyKeyboardRemove())
                else:
                    await message.answer("Произошла ошибка при добавлении валюты")
        except Exception as e:
            logger.error(f"Ошибка при добавлении валюты: {e}")
            await message.answer("Произошла ошибка, попробуйте позже")
    # Очистка состояния
    await state.clear()

# Обработчик кнопки "Удалить валюту"
@dp.message(F.text == "Удалить валюту")
async def delete_currency_start(message: types.Message, state: FSMContext):
    # Проверка, является ли пользователь администратором
    if not await is_admin(message.chat.id):
        await message.answer("Нет доступа к команде")
        return
    # Запрос ввода названия валюты для удаления
    await message.answer("Введите название валюты для удаления:")
    # Установка состояния ожидания ввода названия валюты для удаления
    await state.set_state(CurrencyStates.waiting_for_currency_to_delete)

# Обработчик ввода названия валюты для удаления
@dp.message(CurrencyStates.waiting_for_currency_to_delete)
async def delete_currency(message: types.Message, state: FSMContext):
    # Преобразование введенного названия валюты к верхнему регистру и удаление пробелов
    currency_name = message.text.upper().strip()

    # Отправка запроса на удаление валюты
    async with aiohttp.ClientSession() as session:
        try:
            async with session.delete(f"{CURRENCY_MANAGER_URL}/currencies/{currency_name            }") as resp:
                if resp.status == 200:
                    await message.answer(f"Валюта {currency_name} успешно удалена", reply_markup=types.ReplyKeyboardRemove())
                else:
                    await message.answer("Валюта не найдена или произошла ошибка")
        except Exception as e:
            logger.error(f"Ошибка при удалении валюты: {e}")
            await message.answer("Произошла ошибка, попробуйте позже")
    await state.clear()

# Обработчик кнопки "Изменить курс валюты"
@dp.message(F.text == "Изменить курс валюты")
async def update_currency_start(message: types.Message, state: FSMContext):
    if not await is_admin(message.chat.id):
        await message.answer("Нет доступа к команде")
        return
    await message.answer("Введите название валюты для изменения курса:")
    await state.set_state(CurrencyStates.waiting_for_currency_to_update)

# Обработчик ввода названия валюты для изменения курса
@dp.message(CurrencyStates.waiting_for_currency_to_update)
async def update_currency_name(message: types.Message, state: FSMContext):
    currency_name = message.text.upper().strip()
    await state.update_data(currency_name=currency_name)
    await message.answer("Введите новый курс валюты:")
    await state.set_state(CurrencyStates.waiting_for_currency_rate_to_update)

# Обработчик ввода нового курса
@dp.message(CurrencyStates.waiting_for_currency_rate_to_update)
async def update_currency_rate(message: types.Message, state: FSMContext):
    try:
        rate = float(message.text.replace(",", "."))
        if rate <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Введите корректное положительное число:")
        return

    data = await state.get_data()
    currency_name = data['currency_name']

    async with aiohttp.ClientSession() as session:
        try:
            payload = {"rate": rate}
            async with session.put(f"{CURRENCY_MANAGER_URL}/currencies/{currency_name}", json=payload) as resp:
                if resp.status == 200:
                    await message.answer(f"Курс валюты {currency_name} успешно обновлен", reply_markup=types.ReplyKeyboardRemove())
                else:
                    await message.answer("Валюта не найдена или произошла ошибка")
        except Exception as e:
            logger.error(f"Ошибка при обновлении курса: {e}")
            await message.answer("Произошла ошибка, попробуйте позже")
    await state.clear()

# Обработчик команды /get_currencies
@dp.message(Command("get_currencies"))
async def get_currencies(message: types.Message):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{CURRENCY_MANAGER_URL}/currencies") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data:
                        currencies = "\n".join([f"{name}: {rate}" for name, rate in data.items()])
                        await message.answer(f"Доступные валюты:\n{currencies}")
                    else:
                        await message.answer("Список валют пуст.")
                else:
                    await message.answer("Ошибка при получении списка валют.")
        except Exception as e:
            logger.error(f"Ошибка при получении валют: {e}")
            await message.answer("Произошла ошибка, попробуйте позже")

# Обработчик команды /convert
@dp.message(Command("convert"))
async def convert_start(message: types.Message, state: FSMContext):
    await message.answer("Введите название валюты, которую хотите конвертировать:")
    await state.set_state(CurrencyStates.waiting_for_currency_to_convert)

# Обработчик ввода валюты для конвертации
@dp.message(CurrencyStates.waiting_for_currency_to_convert)
async def convert_currency_name(message: types.Message, state: FSMContext):
    currency_name = message.text.upper().strip()
    await state.update_data(currency_name=currency_name)
    await message.answer("Введите сумму в этой валюте:")
    await state.set_state(CurrencyStates.waiting_for_amount_to_convert)

# Обработчик ввода суммы и выполнение конвертации
@dp.message(CurrencyStates.waiting_for_amount_to_convert)
async def convert_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Введите корректную сумму (больше 0):")
        return

    data = await state.get_data()
    currency_name = data['currency_name']

    async with aiohttp.ClientSession() as session:
        try:
            params = {"currency": currency_name, "amount": amount}
            async with session.get(f"{DATA_MANAGER_URL}/convert", params=params) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    converted = result.get("converted")
                    if converted is not None:
                        await message.answer(f"{amount} {currency_name} = {converted} RUB", reply_markup=types.ReplyKeyboardRemove())
                    else:
                        await message.answer("Ошибка при конвертации")
                else:
                    await message.answer("Ошибка при выполнении запроса конвертации")
        except Exception as e:
            logger.error(f"Ошибка при конвертации: {e}")
            await message.answer("Произошла ошибка, попробуйте позже")
    await state.clear()

# Запуск бота
async def main():
    logger.info("Запуск бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен.")