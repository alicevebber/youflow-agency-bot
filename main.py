from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
import asyncio

from config.settings import settings
from handlers.start import router as start_router
from handlers.services import router as services_router
from handlers.brief import router as brief_router               # ✅ бриф из УСЛУГ
from handlers.main_brief import router as main_brief_router     # ✅ общий бриф из МЕНЮ

# Бот с настройками
bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# Диспетчер с хранилищем состояния
dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.CHAT)

# Подключение всех нужных роутеров
dp.include_routers(
    start_router,
    services_router,
    brief_router,
    main_brief_router  # ✅ подключен общий бриф
)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
