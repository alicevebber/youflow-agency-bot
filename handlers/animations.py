import asyncio
from aiogram.types import Message

WELCOME_LINES = {
    "ru": [
        "▒▒▒▒▒▒▒▒▒▒",  
        "Привет! Это мы",
        "✨ you — flow™ ✨",
        "Создаём выразительные и продуманные <b>digital-продукты</b>."
    ],
    "en": [
        "▒▒▒▒▒▒▒▒▒▒",  
        "Hi! Welcome to",
        "✨ you — flow™ ✨",
        "We create expressive and thoughtful digital products."
    ],
    "kz": [
        "▒▒▒▒▒▒▒▒▒▒",  
        "Сәлем! Қош келдiңiз",
        "✨ you — flow™ ✨",
        "Бiз мәнерлi әрi ойластырылған digital-өнiмдер жасаймыз."
    ]
}

# Быстрый набор по словам (для первой строки с эффектом)
async def typewriter_effect(message: Message, text: str, delay: float = 0.02):
    words = text.split()
    result = ""
    sent = await message.answer("▌")
    for word in words:
        result += (" " if result else "") + word
        await sent.edit_text(result)
        await asyncio.sleep(delay)

async def welcome_sequence(message: Message, lang: str):
    # Первая строка — с эффектом набора
    await typewriter_effect(message, WELCOME_LINES[lang][0])
    await asyncio.sleep(0.3)

    # Остальные строки — обычные, с задержкой между
    for line in WELCOME_LINES[lang][1:]:
        await message.answer(line)
        await asyncio.sleep(0.3)
