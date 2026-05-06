from aiogram import Router
from aiogram.types import Message
from app.database import models
from app.services.matcher import compile_pattern, matches
from app.services.forwarding import forward_message
from app.services.cooldown import CooldownManager
from app.config import settings
import logging

router = Router()
logger = logging.getLogger(__name__)

_cooldown = CooldownManager(settings.COOLDOWN_SECONDS)


@router.message()
async def on_message(message: Message):
    # only handle group/supergroup messages
    if message.chat.type not in ('group', 'supergroup'):
        return
    if message.from_user and message.from_user.is_bot:
        return
    text = message.text or message.caption or ''
    if not text:
        return
    try:
        rows = await models.get_keywords_for_group(message.chat.id)
    except Exception:
        logger.exception('Failed to fetch keywords')
        return
    # store/update group title for lookups from private chat
    try:
        if message.chat.title:
            await models.upsert_group(message.chat.id, message.chat.title)
    except Exception:
        logger.exception('Failed to upsert group title')
    # rows: list of (user_id, keyword, regex_mode)
    for user_id, keyword, regex_mode in rows:
        try:
            pat = compile_pattern(keyword, int(regex_mode))
            if matches(text, pat):
                allowed = await _cooldown.allow(message.chat.id, user_id, keyword)
                if not allowed:
                    logger.debug('Cooldown active for %s %s %s', message.chat.id, user_id, keyword)
                    continue
                # send context message
                context = (
                    f'Matched keyword: {keyword}\n'
                    f'Group: {message.chat.title or message.chat.id}\n'
                    f'Sender: @{message.from_user.username or ""} {message.from_user.full_name}'
                )
                try:
                    await message.bot.send_message(chat_id=user_id, text=context)
                except Exception:
                    logger.exception('Failed to send context to %s', user_id)
                # forward original
                success = await forward_message(message.bot, message.chat.id, message.message_id, user_id)
                if success:
                    logger.info('Forwarded message %s to %s for keyword %s', message.message_id, user_id, keyword)
        except Exception:
            logger.exception('Error processing keyword %s', keyword)
