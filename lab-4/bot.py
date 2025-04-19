import os  # Для доступа к переменным окружения
import logging  # Для логирования событий (например, кто и что сохраняет)
from typing import Dict  # Для аннотации типов словаря

from aiogram import Bot, Dispatcher  # Основные компоненты для создания Telegram-бота
from aiogram.filters import Command  # Фильтр для обработки команд типа /start, /save_currency
from aiogram.fsm.context import FSMContext  # Контекст состояния, хранит промежуточные данные
from aiogram.fsm.state import State, StatesGroup  # Для описания состояний FSM
from aiogram.types import Message  # Объект входящего сообщения от пользователя


# Настройка логирования: будет выводиться информация в консоль (например, сохранённые курсы)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем токен бота из переменной окружения
API_TOKEN = os.getenv("API_TOKEN")

# Создаём экземпляр бота и диспетчера — это "мозг" нашего бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Хранилище курсов валют (у каждого пользователя — свой словарь)
# Словарь вида {user_id: {"USD": 90.5, "EUR": 100.1, ...}}
user_currencies: Dict[int, Dict[str, float]] = {}


# Состояния для команды /save_currency
class SaveCurrencyStates(StatesGroup):
    waiting_for_name = State()  # Ждём, пока пользователь введёт название валюты
    waiting_for_rate = State()  # Ждём курс этой валюты

# Состояния для команды /convert
class ConvertCurrencyStates(StatesGroup):
    waiting_for_currency = State()  # Ждём, какую валюту конвертировать
    waiting_for_amount = State()  # Ждём сумму, которую нужно перевести


# Команда /start
@dp.message(Command("start"))
async def start(message: Message) -> None:
    await message.answer(
        "Привет!🫡\n"
        "Используй команду /save_currency, чтобы сохранить курс валюты.\n"
        "А команду /convert — чтобы выполнить конвертацию."
    )


# Команда /save_currency
@dp.message(Command("save_currency"))
async def save_currency(message: Message, state: FSMContext) -> None:
    await message.answer("Введите название валюты (например, USD, EUR):")
    await state.set_state(SaveCurrencyStates.waiting_for_name) # Переходим к следующему шагу


# Обработка названия валюты
@dp.message(SaveCurrencyStates.waiting_for_name)
async def currency_name(message: Message, state: FSMContext) -> None:
    currency = message.text.upper().strip()  # Приводим к верхнему регистру (usd в USD)
    await state.update_data(currency_name=currency)  # Сохраняем в хранилище
    await message.answer(f"Введите курс {currency} к рублю:")
    await state.set_state(SaveCurrencyStates.waiting_for_rate)


# Обработка курса валюты
@dp.message(SaveCurrencyStates.waiting_for_rate)
async def currency_rate(message: Message, state: FSMContext) -> None:
    try:
        # Преобразуем ввод в число и заменяем запятую на точку
        rate = float(message.text.replace(",", "."))
        if rate <= 0:
            raise ValueError("Курс должен быть положительным")

        # Получаем сохранённое название валюты
        data = await state.get_data()
        currency = data["currency_name"]
        user_id = message.from_user.id

        # Сохраняем курс валюты для этого пользователя
        user_currencies.setdefault(user_id, {})[currency] = rate
        logger.info(f"Пользователь {user_id} сохранил курс: 1 {currency} = {rate} RUB")

        await message.answer(f"Сохранено: 1 {currency} = {rate:.2f} RUB")
        await state.clear()  # Завершаем FSM

    except ValueError:
        await message.answer("Ошибка! Введите корректный числовой курс (например: 90.5):")



# Команда /convert
@dp.message(Command("convert"))
async def convert(message: Message, state: FSMContext) -> None:
    await message.answer("Введите название валюты для конвертации (например, USD, EUR):")
    await state.set_state(ConvertCurrencyStates.waiting_for_currency)


# Обработка названия валюты для конвертации
@dp.message(ConvertCurrencyStates.waiting_for_currency)
async def convert_currency(message: Message, state: FSMContext) -> None:
    currency = message.text.upper().strip()
    user_id = message.from_user.id

    # Проверяем, есть ли у пользователя сохранённые валюты и нужная из них
    if user_id in user_currencies and currency in user_currencies[user_id]:
        await state.update_data(currency=currency)
        await message.answer(f"Введите сумму в {currency}, которую нужно конвертировать:")
        await state.set_state(ConvertCurrencyStates.waiting_for_amount)
    else:
        # Формируем список всех сохранённых валют пользователя
        if user_id in user_currencies and user_currencies[user_id]:
            available = "\n".join(
                f"• {cur} = {rate:.2f} RUB"
                for cur, rate in user_currencies[user_id].items()
            )
            await message.answer(
                f"❌ Валюта {currency} не найдена.\n"
                f"Вот список доступных валют, которые вы сохранили:\n\n{available}"
            )
        else:
            await message.answer(
                f"❌ Валюта {currency} не найдена.\n"
                f"Вы ещё не сохраняли ни одной валюты. Используйте команду /save_currency."
            )
        await state.clear()


# Обработка суммы для конвертации
@dp.message(ConvertCurrencyStates.waiting_for_amount)
async def process_convert_amount(message: Message, state: FSMContext) -> None:
    try:
        amount = float(message.text.replace(",", "."))
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")

        user_id = message.from_user.id
        data = await state.get_data()
        currency = data["currency"]
        rate = user_currencies[user_id][currency]
        result = amount * rate

        await message.answer(
            f"Конвертация:\n"
            f"{amount:.2f} {currency} = {result:.2f} RUB\n"
            f"Курс: 1 {currency} = {rate:.2f} RUB"
        )
        await state.clear()  # Завершаем FSM

    except ValueError:
        await message.answer("Ошибка! Введите корректную сумму (например: 100 или 50.5):")


async def main() -> None:
    await dp.start_polling(bot)  # Запускаем бота (начинает слушать входящие сообщения)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())  # Запуск основного цикла

