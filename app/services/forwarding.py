import logging
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramRetryAfter, TelegramBadRequest

logger = logging.getLogger(__name__)

async def forward_message(bot: Bot, from_chat_id: int, message_id: int, to_user_id: int) -> bool:
    try:
        await bot.forward_message(chat_id=to_user_id, from_chat_id=from_chat_id, message_id=message_id)
        logger.info('Forwarded message %s from %s to %s', message_id, from_chat_id, to_user_id)
        return True
    except TelegramRetryAfter as e:
        logger.warning('RetryAfter %s when forwarding to %s', e.retry_after, to_user_id)
    except TelegramBadRequest as e:
        logger.warning('BadRequest when forwarding to %s: %s', to_user_id, e)
    except TelegramAPIError as e:
        logger.exception('Telegram API error when forwarding to %s: %s', to_user_id, e)
    return False
