import asyncio
from app.config import settings
from app.utils.logger import setup_logging
from app.database.db import Database
from aiogram import Bot, Dispatcher
import logging

setup_logging()
logger = logging.getLogger(__name__)


async def main():
    if not settings.BOT_TOKEN:
        raise RuntimeError('BOT_TOKEN is not set in environment or .env')

    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    # Initialize database
    await Database.init(settings.SQLITE_PATH)

    # Register handlers
    from app.handlers import register_all  # noqa: E402
    register_all(dp)

    logger.info('Starting bot polling')
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Interrupted')
