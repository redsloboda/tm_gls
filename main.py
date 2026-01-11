import asyncio
import csv
import os
from datetime import datetime
from typing import Any

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
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
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📅 Записать клиента", web_app=WebAppInfo(url=WEBAPP_URL))]],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    await message.answer(
        "<b>🚗 АвтоЗапись</b>\n\n"
        "Нажмите кнопку ниже, чтобы открыть форму записи клиента.",
        reply_markup=kb
    )

@router.message(F.web_app_data)
async def webapp_data_handler(message: Message, bot: Bot):
    data: dict[str, Any] = message.web_app_data
    try:
        # Парсим данные из Mini App
        booking_data = {
            "date": data.get("date", ""),
            "time": data.get("time", ""),
            "car_number": data.get("car_number", ""),
            "car_model": data.get("car_model", ""),
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
        
        await message.answer(
            f"✅ <b>Запись создана!</b>\n\n"
            f"📅 <b>Дата:</b> {booking_data['date']}\n"
            f"🕒 <b>Время:</b> {booking_data['time']}\n"
            f"🚗 <b>Номер:</b> {booking_data['car_number']}\n"
            f"🚙 <b>Марка:</b> {booking_data['car_model']}\n\n"
            f"👤 Сотрудник: {booking_data['employee']}"
        )
    except Exception as e:
        await message.answer("❌ Ошибка при сохранении записи. Попробуйте снова.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":

    asyncio.run(main())

