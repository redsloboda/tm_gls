import asyncio
import csv
import json
import os
from datetime import datetime, timedelta
from typing import Any

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL_WASH = "https://redsloboda.github.io/tm_gls/?service=wash"  # Автомойка
WEBAPP_URL_SERVICE = "https://redsloboda.github.io/tm_gls/?service=service"  # Автосервис

# Google Calendar настройки (замени на свои)
SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_ID = 'primary'  # или ID твоего календаря

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()
router = Router()
dp.include_router(router)

def create_google_event(summary: str, start_time: str, service_type: str):
    """Создаёт событие в Google Calendar"""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    service = build('calendar', 'v3', credentials=creds)
    
    event = {
        'summary': f'{service_type}: {summary}',
        'description': f'Марка: {summary}',
        'start': {'dateTime': start_time, 'timeZone': 'Europe/Moscow'},
        'end': {'dateTime': (datetime.fromisoformat(start_time) + timedelta(hours=1)).isoformat(), 'timeZone': 'Europe/Moscow'},
    }
    
    event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    return event.get('htmlLink')

@router.message(CommandStart())
async def start_handler(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚿 Автомойка", web_app=WebAppInfo(url=WEBAPP_URL_WASH))],
        [InlineKeyboardButton(text="🛠 Автосервис", web_app=WebAppInfo(url=WEBAPP_URL_SERVICE))]
    ])
    await message.answer(
        "<b>🚗 АвтоЗапись</b>\n\n"
        "Выбери тип услуги:",
        reply_markup=kb
    )

@router.message(F.web_app_data)
async def webapp_data_handler(message: Message):
    booking_json = json.loads(message.web_app_data.data)
    
    service_type = booking_json.get("service", "Неизвестно")
    date_str = booking_json.get("date", "")
    time_str = booking_json.get("time", "")
    car_model = booking_json.get("car_model", "")
    
    # Формат даты: 13-01-2026 13:00
    date_obj = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    formatted_datetime = date_obj.strftime("%d-%m-%Y %H:%M")
    full_datetime = date_obj.isoformat()
    
    booking_data = {
        "service": service_type,
        "date": formatted_datetime,
        "car_model": car_model,
        "employee": message.from_user.full_name,
        "user_id": message.from_user.id,
        "timestamp": datetime.now().isoformat()
    }
    
    # CSV
    with open("bookings.csv", "a", newline="", encoding="utf-8") as f:
        if os.path.getsize("bookings.csv") == 0:
            writer = csv.DictWriter(f, fieldnames=booking_data.keys())
            writer.writeheader()
        writer = csv.DictWriter(f, fieldnames=booking_data.keys())
        writer.writerow(booking_data)
    
    # Google Calendar
    try:
        event_link = create_google_event(car_model, full_datetime, service_type)
        calendar_text = f"\n🔗 <a href='{event_link}'>В календаре</a>"
    except:
        calendar_text = "\n❌ Ошибка календаря"
    
    await message.answer(
        f"✅ <b>Запись создана!</b>\n\n"
        f"🏷 <b>{service_type}</b>\n"
        f"📅 <b>{formatted_datetime}</b>\n"
        f"🚙 <b>{car_model}</b>{calendar_text}\n\n"
        f"👤 {booking_data['employee']}"
    )

async def main():
    print("🚀 Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
