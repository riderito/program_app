from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram import F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получение токена из переменных окружения
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

# Инициализация бота и диспетчера
bot = Bot(token=bot_token)
dp = Dispatcher()


# Определение состояний FSM
class CurrencyStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_rate = State()


# Обработчик команды /start
@dp.message(Command('start'))
async def start_command(message: types.Message):
    await message.answer("Привет! Используй /save_currency для сохранения курса валют")


# Обработчик команды /save_currency
@dp.message(Command('save_currency'))
async def save_currency_command(message: Message, state: FSMContext):
    await message.answer("Введите название валюты (например, USD, EUR):")
    await state.set_state(CurrencyStates.waiting_for_name)


# Обработчик ввода названия валюты
@dp.message(CurrencyStates.waiting_for_name)
async def process_currency_name(message: Message, state: FSMContext):
    await state.update_data(currency_name=message.text.upper().strip())
    await message.answer(f"Введите курс {message.text.upper().strip()} к рублю:")
    await state.set_state(CurrencyStates.waiting_for_rate)


# Обработчик ввода курса валюты
@dp.message(CurrencyStates.waiting_for_rate)
async def process_currency_rate(message: Message, state: FSMContext):
    try:
        rate = float(message.text.replace(',', '.'))
        data = await state.get_data()
        currency_name = data['currency_name']

        logger.info(f"Сохранен курс: 1 {currency_name} = {rate} RUB")
        await message.answer(f"Сохранено: 1 {currency_name} = {rate} RUB")
        await state.clear()

    except ValueError:
        await message.answer("Ошибка! Введите число (например: 90.5):")


# Запуск бота (обновленный способ для aiogram 3.x)
async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())