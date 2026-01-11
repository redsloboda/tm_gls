import asyncio
import csv
import json
import os
from datetime import datetime, timedelta

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

# ТВОИ календари (замени на реальные ID)
CALENDAR_ID_WASH = 'мойка_calendar_id@group.calendar.google.com'  # ID календаря автомойки
CALENDAR_ID_SERVICE = 'сервис_calendar_id@group.calendar.google.com'  # ID календаря автосервиса

WEBAPP_URL_WASH = "https://redsloboda.github.io/tm_gls/?service=wash"
WEBAPP_URL_SERVICE = "https://redsloboda.github.io/tm_gls/?service=service"

SCOPES = ['https://www.googleapis.com/auth/calendar']

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()
router = Router()
dp.include_router(router)

def create_calendar_event(summary: str, start_time: str, calendar_id: str):
    """Создаёт событие в указанном календаре"""
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
        'summary': summary,
        'description': f'Автосервис запись через Telegram бот',
        'start': {'dateTime': start_time, 'timeZone': 'Europe/Moscow'},
        'end': {'dateTime': (datetime.fromisoformat(start_time) + timedelta(hours=1)).isoformat(), 'timeZone': 'Europe/Moscow'},
        'colorId': '1'  # Зелёный для мойки, оранжевый для сервиса можно настроить
    }
    
    event = service.events().insert(calendarId=calendar_id, body=event).execute()
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
    
    # Формат: 13-01-2026 13:00
    date_obj = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    formatted_datetime = date_obj.strftime("%d-%m-%Y %H:%M")
    full_datetime = date_obj.isoformat()
    
    # Выбираем календарь по типу услуги
    calendar_id = CALENDAR_ID_WASH if service_type == 'wash' else CALENDAR_ID_SERVICE
    
    booking_data = {
        "service": service_type,
        "date": formatted_datetime,
        "car_model": car_model,
        "calendar": calendar_id,
        "employee": message.from_user.full_name,
        "user_id": message.from_user.id,
        "timestamp": datetime.now().isoformat()
    }
    
    # Сохраняем CSV
    with open("bookings.csv", "a", newline="", encoding="utf-8") as f:
        if os.path.getsize("bookings.csv") == 0:
            writer = csv.DictWriter(f, fieldnames=booking_data.keys())
            writer.writeheader()
        writer = csv.DictWriter(f, fieldnames=booking_data.keys())
        writer.writerow(booking_data)
    
    # Google Calendar
    try:
        event_link = create_calendar_event(f"{service_type.title()}: {car_model}", full_datetime, calendar_id)
        calendar_text = f"\n🔗 <a href='{event_link}'>Открыть в календаре</a>"
    except Exception as e:
        print(f"Ошибка календаря: {e}")
        calendar_text = "\n📅 Будет в CSV"
    
    await message.answer(
        f"✅ <b>{service_type.title()}</b>\n\n"
        f"📅 <b>{formatted_datetime}</b>\n"
        f"🚙 <b>{car_model}</b>{calendar_text}\n\n"
        f"👤 {booking_data['employee']}"
    )

async def main():
    print("🚀 Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
