from aiogram import Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    Message
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from handlers.service_details import SERVICE_DETAILS as service_details
from handlers.service_data import services, HEADINGS
from handlers.brief_data import BRIEF_QUESTIONS
import translations

router = Router()

class BriefForm(StatesGroup):
    waiting_for_answer = State()

def escape_md(text: str) -> str:
    special_chars = r'\_[]()~`>#+-=|{}.!'
    for char in special_chars:
        text = text.replace(char, f"\\{char}")
    return text

# 🔹 Отображение списка сервисов
@router.callback_query(lambda c: c.data == "services")
async def show_services(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")

    menu_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=translations.TEXT[lang]["menu_button"])]],
        resize_keyboard=True,
        is_persistent=True
    )

    await callback.message.answer(HEADINGS[lang], reply_markup=menu_keyboard)

    for key, service in services[lang].items():
        text = (
            f"{escape_md(service['title'])}\n"
            f"{escape_md(service['description'])}\n"
            f"{escape_md(service['duration'])}\n"
            f"💰 ||{escape_md(service['price'])}||"
        )
        buttons = [
            [
                InlineKeyboardButton(
                    text={"ru": "📄 Подробнее", "en": "📄 More info", "kz": "📄 Толығырақ"}[lang],
                    callback_data=f"details_{key}"
                ),
                InlineKeyboardButton(
                    text={"ru": "📩 Отправить заявку", "en": "📩 Send request", "kz": "📩 Өтінім жіберу"}[lang],
                    callback_data=f"request_{key}"
                )
            ]
        ]
        await callback.message.answer(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
            parse_mode="MarkdownV2"
        )

# 🔹 Обработка запроса на заполнение брифа
@router.callback_query(lambda c: c.data.startswith("request_"))
async def handle_request(callback: CallbackQuery, state: FSMContext):
    service_id = callback.data.split("request_")[-1]
    await state.update_data(request_service_id=service_id)
    data = await state.get_data()
    lang = data.get("lang", "ru")

    service_name = services[lang].get(service_id, {}).get("title", "[unknown service]")
    user = callback.from_user
    contact_info = f"@{user.username}" if user.username else f"{user.first_name or 'Без имени'} (id: {user.id})"

    await state.update_data(
        current_question=0,
        answers=[],
        current_service_id=service_id,
        user_contact=contact_info
    )

    questions = BRIEF_QUESTIONS[lang][service_id]

    confirm_text = {
        "ru": "Вы выбрали услугу:",
        "en": "You selected the service:",
        "kz": "Сіз таңдаған қызмет:"
    }[lang]

    await callback.message.answer("✔️")

    await callback.message.answer(
        f"{confirm_text}\n\n*{escape_md(service_name)}*\n" +
        {
            "ru": "👉 Ответьте на *6 коротких вопросов* для брифа",
            "en": "👉 Please answer *6 short questions* for the brief",
            "kz": "👉 Бриф үшін *6 қысқа сұраққа* жауап беріңіз"
        }[lang],
        parse_mode="MarkdownV2"
    )

    await callback.message.answer(questions[0])
    await state.set_state(BriefForm.waiting_for_answer)

# 🔹 Быстрая заявка без брифа
@router.callback_query(lambda c: c.data == "quick_request")
async def handle_quick_request(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    service_id = data.get("request_service_id")
    lang = data.get("lang", "ru")

    service_name = services[lang].get(service_id, {}).get("title", "[unknown service]")

    await callback.message.answer("✔️")

    confirm_text = {
        "ru": "Мы свяжемся с вами, чтобы уточнить детали✨.",
        "en": "We'll contact you shortly to clarify the details✨.",
        "kz": "Біз сізбен байланысып, егжей-тегжейін нақтылаймыз✨."
    }[lang]

    full_message = escape_md(confirm_text) + f"\n{escape_md({'ru': 'Вы выбрали', 'en': 'You selected', 'kz': 'Сіз таңдадыңыз'}[lang])}: *{escape_md(service_name)}*"

    await callback.message.answer(full_message, parse_mode="MarkdownV2")

# 🔹 Подробнее об услуге
@router.callback_query(lambda c: c.data.startswith("details_"))
async def handle_details(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    service_id = callback.data.split("details_")[-1]

    text = service_details[lang].get(service_id, {
        "ru": "Информация временно недоступна.",
        "en": "Information temporarily unavailable.",
        "kz": "Ақпарат уақытша қолжетімсіз."
    }[lang])

    request_text = {
        "ru": "📩 Оставить заявку",
        "en": "📩 Send request",
        "kz": "📩 Өтінім жіберу"
    }[lang]

    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=request_text, callback_data=f"request_{service_id}")]
        ]
    )

    await callback.message.answer(text, reply_markup=buttons)
