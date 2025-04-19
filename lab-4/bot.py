import os
import logging
from typing import Dict

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получение токена бота из переменной окружения
API_TOKEN = os.getenv("API_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Хранилище курсов валют (в реальном приложении — база данных)
user_currencies: Dict[int, Dict[str, float]] = {}

# Состояния для команды /save_currency
class SaveCurrencyStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_rate = State()

# Состояния для команды /convert
class ConvertCurrencyStates(StatesGroup):
    waiting_for_currency = State()
    waiting_for_amount = State()


# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! 👋\n"
        "Используй команду /save_currency, чтобы сохранить курс валюты.\n"
        "А команду /convert — чтобы выполнить конвертацию."
    )


# Команда /save_currency — начало
@dp.message(Command("save_currency"))
async def cmd_save_currency(message: Message, state: FSMContext) -> None:
    await message.answer("Введите название валюты (например, USD, EUR):")
    await state.set_state(SaveCurrencyStates.waiting_for_name)


# Обработка названия валюты
@dp.message(SaveCurrencyStates.waiting_for_name)
async def process_currency_name(message: Message, state: FSMContext) -> None:
    currency = message.text.upper().strip()
    await state.update_data(currency_name=currency)
    await message.answer(f"Введите курс {currency} к рублю:")
    await state.set_state(SaveCurrencyStates.waiting_for_rate)


# Обработка курса валюты
@dp.message(SaveCurrencyStates.waiting_for_rate)
async def process_currency_rate(message: Message, state: FSMContext) -> None:
    try:
        rate = float(message.text.replace(",", "."))
        if rate <= 0:
            raise ValueError("Курс должен быть положительным")

        data = await state.get_data()
        currency = data["currency_name"]
        user_id = message.from_user.id

        user_currencies.setdefault(user_id, {})[currency] = rate
        logger.info(f"Пользователь {user_id} сохранил курс: 1 {currency} = {rate} RUB")

        await message.answer(f"✅ Сохранено: 1 {currency} = {rate:.2f} RUB")
        await state.clear()

    except ValueError:
        await message.answer("Ошибка! Введите корректный числовой курс (например: 90.5):")


# Команда /convert — начало
@dp.message(Command("convert"))
async def cmd_convert(message: Message, state: FSMContext) -> None:
    await message.answer("Введите название валюты для конвертации (например, USD, EUR):")
    await state.set_state(ConvertCurrencyStates.waiting_for_currency)


# Обработка названия валюты для конвертации
@dp.message(ConvertCurrencyStates.waiting_for_currency)
async def process_convert_currency(message: Message, state: FSMContext) -> None:
    currency = message.text.upper().strip()
    user_id = message.from_user.id

    if user_id in user_currencies and currency in user_currencies[user_id]:
        await state.update_data(currency=currency)
        await message.answer(f"Введите сумму в {currency}, которую нужно конвертировать:")
        await state.set_state(ConvertCurrencyStates.waiting_for_amount)
    else:
        await message.answer(f"⚠️ Валюта {currency} не найдена. Сначала сохраните её с помощью /save_currency.")
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
            f"💱 Конвертация:\n"
            f"{amount:.2f} {currency} = {result:.2f} RUB\n"
            f"Курс: 1 {currency} = {rate:.2f} RUB"
        )
        await state.clear()

    except ValueError:
        await message.answer("Ошибка! Введите корректную сумму (например: 100 или 50.5):")


# Основной запуск бота
async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
