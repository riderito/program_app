from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os
import logging
from typing import Dict

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получение токена из переменных окружения
bot_token = os.getenv('API_TOKEN')

# Инициализация бота и диспетчера
bot = Bot(token=bot_token)
dp = Dispatcher()

# Предполагаем, что у нас есть словарь с курсами валют
# В реальном проекте лучше использовать базу данных
user_currencies: Dict[int, Dict[str, float]] = {
    # Пример данных: {user_id: {"USD": 90.5, "EUR": 100.2}}
}

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


# Обработчик команды /convert
@dp.message(Command('convert'))
async def cmd_convert(message: types.Message, state: FSMContext):
    await message.answer("Введите название валюты для конвертации (например, USD, EUR):")
    await state.set_state(ConvertStates.waiting_for_currency)


# Обработчик ввода названия валюты
@dp.message(ConvertStates.waiting_for_currency)
async def process_currency_name(message: types.Message, state: FSMContext):
    currency = message.text.upper().strip()
    user_id = message.from_user.id

    # Проверяем, есть ли такая валюта у пользователя
    if user_id in user_currencies and currency in user_currencies[user_id]:
        await state.update_data(currency=currency)
        await message.answer(f"Введите сумму в {currency} для конвертации в рубли:")
        await state.set_state(ConvertStates.waiting_for_amount)
    else:
        await message.answer(f"Валюта {currency} не найдена. Используйте /save_currency чтобы добавить курс.")
        await state.clear()


# Обработчик ввода суммы
@dp.message(ConvertStates.waiting_for_amount)
async def process_currency_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(',', '.'))
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")

        user_data = await state.get_data()
        currency = user_data['currency']
        user_id = message.from_user.id

        rate = user_currencies[user_id][currency]
        converted = amount * rate

        await message.answer(
            f"Результат конвертации:\n"
            f"{amount:.2f} {currency} = {converted:.2f} RUB\n"
            f"Курс: 1 {currency} = {rate:.2f} RUB"
        )

    except ValueError:
        await message.answer("Ошибка! Введите корректную сумму (например: 100 или 50.5):")
        return  # Остаемся в том же состоянии

    await state.clear()


# Запуск бота (обновленный способ для aiogram 3.x)
async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())