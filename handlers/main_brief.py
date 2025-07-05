from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from handlers.main_brief_data import BRIEF_QUESTIONS

router = Router()

# ✅ Уникальное состояние для общего брифа
class MainBriefForm(StatesGroup):
    waiting_for_general_answer = State()

@router.callback_query(lambda c: c.data == "request")
async def start_brief(callback: CallbackQuery, state: FSMContext):
    lang = (await state.get_data()).get("lang", "ru")
    await state.update_data(current_question=0, answers=[])

    await callback.message.answer("✔️")
    await callback.message.answer({
        "ru": "👉 Ответьте на <b>6 коротких вопросов</b> для брифа",
        "en": "👉 Please answer <b>6 short questions</b> for the brief",
        "kz": "👉 Бриф үшін <b>6 қысқа сұраққа</b> жауап беріңіз"
    }[lang])

    questions = BRIEF_QUESTIONS[lang]
    await callback.message.answer(questions[0])
    await state.set_state(MainBriefForm.waiting_for_general_answer)  # ✅ правильно

@router.message(MainBriefForm.waiting_for_general_answer)  # ✅ правильно
async def handle_brief_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    answers = data.get("answers", [])
    index = data.get("current_question", 0)

    answers.append(message.text)
    index += 1

    await state.update_data(answers=answers, current_question=index)

    questions = BRIEF_QUESTIONS[lang]
    if index < len(questions):
        await message.answer(questions[index])
    else:
        thank_you_text = {
            "ru": "Супер!️\nСкоро мы свяжемся для <b>подтверждения заказа</b>!✨",
            "en": "Thank you! You're amazing.️\nWe will contact you soon to <b>confirm your order</b>✨",
            "kz": "Рақмет! Сіз кереметсіз.\nТапсырысыңызды растау үшін жақын <b>арада сізбен хабарласамыз</b>✨"
        }.get(lang, "Thank you!")

        await message.answer("✍🏼️")
        await message.answer(thank_you_text)
        await state.clear()
