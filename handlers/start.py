from aiogram import Router, F
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart

from handlers.main_brief import start_brief
from handlers.animations import welcome_sequence
import translations

router = Router()

# 🔹 Хендлер команды /start — выбор языка
@router.message(CommandStart())
async def select_language(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇷🇺 Русский"), KeyboardButton(text="🇬🇧 English"), KeyboardButton(text="🇰🇿 Қазақша")]
        ],
        resize_keyboard=True
    )
    await message.answer("💬 Выберите язык / Select language / Тілді таңдаңыз:", reply_markup=keyboard)

# 🔹 Хендлер выбора языка и приветствие с анимацией
@router.message(F.text.in_(["🇷🇺 Русский", "🇬🇧 English", "🇰🇿 Қазақша"]))
async def send_welcome(message: Message, state: FSMContext):
    lang_map = {
        "🇷🇺 Русский": "ru",
        "🇬🇧 English": "en",
        "🇰🇿 Қазақша": "kz"
    }
    lang = lang_map.get(message.text, "ru")
    await state.update_data(lang=lang)

    await message.answer("⌛", reply_markup=ReplyKeyboardRemove())
    await welcome_sequence(message, lang=lang)
    await send_main_menu(message, lang)

# 🔹 Функция отображения главного меню
async def send_main_menu(message: Message, lang: str):
    buttons = [
        [InlineKeyboardButton(text=translations.TEXT[lang]["menu_services"], callback_data="services")],
        [InlineKeyboardButton(text=translations.TEXT[lang]["menu_about"], callback_data="about")],
        [InlineKeyboardButton(text=translations.TEXT[lang]["menu_site"], url="https://youflow.agency/")],
        [InlineKeyboardButton(text=translations.TEXT[lang]["menu_request"], callback_data="request")],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(translations.TEXT[lang]["menu_title"], reply_markup=keyboard)

# 🔹 Хендлер для кнопки "Оставить заявку" из главного меню
@router.callback_query(lambda c: c.data == "request")
async def handle_main_menu_request(callback: CallbackQuery, state: FSMContext):
    await start_brief(callback, state)

# 🔹 Возврат в меню по кнопке "назад"
@router.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    await send_main_menu(callback.message, lang)
    await callback.answer()

# 🔹 Поддержка текстовой кнопки "Меню" в чате
@router.message(F.text.in_([
    translations.TEXT["ru"]["menu_button"],
    translations.TEXT["en"]["menu_button"],
    translations.TEXT["kz"]["menu_button"]
]))
async def handle_main_menu_button(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    await send_main_menu(message, lang)

# 🔹 Хендлер для кнопки "О нас"
@router.callback_query(lambda c: c.data == "about")
async def handle_about(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")

    about_text = {
        "ru": "✨",
        "en": "✨",
        "kz": "✨"
    }[lang]

    body_text = {
        "ru": (
            "<b>you — flow™</b> — это продуктовое-агентство с острым глазом и глубокой экспертизой.\n\n"
            "Мы создаём визуальные и UX-решения, которые <b>усиливают бренды</b> и вдохновляют команды.\n\n"
            "От  первых экранов до масштабируемых дизайн-систем — мы подключаемся туда, <b>где важен результат</b>, а не просто макет."
        ),
        "en": (
            "<b>you — flow™</b> is a product agency with sharp vision and deep expertise.\n\n"
            "We create visual and UX solutions that <b>strengthen brands</b> and inspire teams.\n\n"
            "From the first screens to scalable design systems — we step in where <b>results matter</b>, not just mockups."
        ),
        "kz": (
            "<b>you — flow™</b> — көзі және үлкен тәжірибесі бар өнім агенттігі болып табылады.\n\n"
            "Біз брендтерді күшейтіп, командаларды шабыттандыратын визуалды және UX-шешімдер жасаймыз.\n\n"
            "Алқашқы экрандардан масштабталатын дизайн жүйелеріне дейін — біз нәтиже маңызды болған жерде қосыламыз."
        )
    }

    await callback.message.answer(about_text)
    await callback.message.answer(body_text, parse_mode="HTML")
