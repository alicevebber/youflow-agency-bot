from aiogram import Router
from aiogram.types import CallbackQuery, Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from handlers.brief_data import BRIEF_QUESTIONS

router = Router()

class BriefForm(StatesGroup):
    waiting_for_answer = State()

@router.callback_query(lambda c: c.data.startswith("fill_brief_"))
async def start_brief(callback: CallbackQuery, state: FSMContext):
    lang = (await state.get_data()).get("lang", "ru")
    service_id = callback.data.split("fill_brief_")[-1]

    await state.update_data(
        current_question=0,
        answers=[],
        current_service_id=service_id
    )

    questions = BRIEF_QUESTIONS[lang][service_id]

    await callback.message.answer("✔️")
    await callback.message.answer({
        "ru": "👉 Ответьте на 6 коротких вопросов для этой услуги",
        "en": "👉 Please answer 6 short questions for this service",
        "kz": "👉 Бұл қызмет бойынша 6 қысқа сұраққа жауап беріңіз"
    }[lang])
    await callback.message.answer(questions[0])
    await state.set_state(BriefForm.waiting_for_answer)

@router.message(BriefForm.waiting_for_answer)
async def process_brief_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    service_id = data.get("current_service_id")

    if not service_id:
        await message.answer("⚠️ Ошибка: не найдена услуга.")
        await state.clear()
        return

    answers = data.get("answers", [])
    current_index = data.get("current_question", 0)

    answers.append(message.text)
    current_index += 1

    await state.update_data(answers=answers, current_question=current_index)

    questions = BRIEF_QUESTIONS[lang][service_id]

    if current_index < len(questions):
        await message.answer(questions[current_index])
    else:
        thank_you_text = {
            "ru": "Отлично, спасибо!️\nСкоро мы свяжемся для <b>подтверждения заказа</b>!✨",
            "en": "Thank you! You're amazing.️\nWe will contact you soon to <b>confirm your order</b>✨",
            "kz": "Рақмет! Сіз кереметсіз.\nТапсырысыңызды растау үшін жақын <b>арада сізбен хабарласамыз</b>✨"
        }.get(lang, "Thank you!")

        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text={
                    "ru": "📌 Меню",
                    "en": "📌 Menu",
                    "kz": "📌 Мәзір"
                }[lang])]
            ],
            resize_keyboard=True,
            input_field_placeholder={
                "ru": "Выберите действие",
                "en": "Choose an action",
                "kz": "Әрекетті таңдаңыз"
            }[lang]
        )

        await message.answer("✍🏼️")
        await message.answer(thank_you_text, reply_markup=keyboard)
        await state.clear()
