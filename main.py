import asyncio
import csv
import os
from datetime import datetime
from typing import Any

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = "https://redsloboda.github.io/tm_gls/"

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()
router = Router()
dp.include_router(router)

@router.message(CommandStart())
async def start_handler(message: Message):
    print(f"Получено /start от {message.from_user.id}")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Записать клиента", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])
    await message.answer(
        "<b>🚗 АвтоЗапись</b>\n\n"
        "Нажми кнопку ниже для записи:",
        reply_markup=kb
    )

@router.message(F.web_app_data)
async def webapp_data_handler(message: Message):
    print(f"✅ Получены данные: {message.web_app_data.data}")
    data: dict[str, Any] = message.web_app_data
    booking_data = {
        "date": data.get("date", ""),
        "time": data.get("time", ""),
        "car_number": data.get("car_number", ""),
        "car_model": data.get("car_model", ""),
        "employee": message.from_user.full_name,
        "user_id": message.from_user.id,
        "timestamp": datetime.now().isoformat()
    }
    
    with open("bookings.csv", "a", newline="", encoding="utf-8") as f:
        if os.path.getsize("bookings.csv") == 0:
            writer = csv.DictWriter(f, fieldnames=booking_data.keys())
            writer.writeheader()
        writer = csv.DictWriter(f, fieldnames=booking_data.keys())
        writer.writerow(booking_data)
    
    await message.answer(
        f"✅ <b>Запись создана!</b>\n\n"
        f"📅 <b>{booking_data['date']} {booking_data['time']}</b>\n"
        f"🚗 <b>{booking_data['car_number']} {booking_data['car_model']}</b>\n\n"
        f"👤 {booking_data['employee']}"
    )

async def main():
    print("🚀 Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
