import asyncio
import csv
import json
import os
from datetime import datetime

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
        "Нажми кнопку ниже:",
        reply_markup=kb
    )

@router.message(F.web_app_data)
async def webapp_data_handler(message: Message):
    print(f"✅ Получены данные: {message.web_app_data.data}")
    
    # Парсим JSON данные из WebAppData
    booking_json = json.loads(message.web_app_data.data)
    
    booking_data = {
        "date": booking_json.get("date", ""),
        "time": booking_json.get("time", ""),
        "car_number": booking_json.get("car_number", ""),
        "car_model": booking_json.get("car_model", ""),
        "employee": message.from_user.full_name,
        "user_id": message.from_user.id,
        "timestamp": datetime.now().isoformat()
    }
    
    # Сохраняем в CSV
    file_exists = os.path.exists("bookings.csv")
    with open("bookings.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=booking_data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(booking_data)
    
    print(f"📄 Сохранено в bookings.csv")
    
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
