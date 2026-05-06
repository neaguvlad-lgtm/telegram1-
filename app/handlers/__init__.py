from aiogram import Dispatcher
from .start import router as start_router
from .keywords import router as keywords_router
from .messages import router as messages_router


def register_all(dp: Dispatcher):
    dp.include_router(start_router)
    dp.include_router(keywords_router)
    dp.include_router(messages_router)
