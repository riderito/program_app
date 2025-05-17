import asyncio
import logging
import os
import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv("API_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message(F.text == "Получить данные")
async def get_aggregated_data(message: Message):
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:5001/aggregate") as response:
            data = await response.json()

    result = data.get("Результат агрегации", {})
    service_2_text = result.get("Ответ от сервиса 2", {}).get("service_2", "")
    service_3_text = result.get("Ответ от сервиса 3", {}).get("service_3", "")

    final_text = f"{service_2_text} {service_3_text}"

    await message.answer(f"Ответ от агрегатора:\n{final_text}")


@dp.message()
async def show_menu(message: Message):
    kb = ReplyKeyboardBuilder()
    kb.button(text="Получить данные")
    await message.answer("Выберите действие:", reply_markup=kb.as_markup(resize_keyboard=True))


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
