from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from app.database import models
import logging

router = Router()
logger = logging.getLogger(__name__)


def _parse_keywords_from_text(text: str):
    parts = text.split()
    # the first is the command
    return [p.strip() for p in parts[1:] if p.strip()]


def _parse_group_and_keywords(text: str):
    """Support form: "Group Name" keyword1 keyword2 (used in private chat)
    Group name must be quoted with double quotes. Returns (group_name, [keywords]) or (None, None)
    """
    text = text.strip()
    if not text:
        return None, None
    if text[0] != '"':
        return None, None
    try:
        end = text.index('"', 1)
    except ValueError:
        return None, None
    group = text[1:end]
    rest = text[end+1:].strip()
    kws = [p for p in rest.split() if p]
    return group, kws


@router.message(Command('add'))
async def cmd_add(message: Message):
    # Support adding from private: /add "Group Name" kw1 kw2
    if message.chat.type == 'private':
        body = (message.text or '').split(' ', 1)
        if len(body) < 2:
            await message.reply('Usage in private: /add "Group Name" keyword1 keyword2')
            return
        group_name, kws = _parse_group_and_keywords(body[1])
        if not group_name or not kws:
            await message.reply('Invalid format. Use: /add "Group Name" keyword1 keyword2')
            return
        # find group id by title
        found = await models.find_group_by_title(group_name)
        if not found:
            await message.reply(f'Group with title "{group_name}" not found. Make sure the bot has seen the group and the title matches exactly.')
            return
        group_id = found[0]
    else:
        kws = _parse_keywords_from_text(message.text or '')
        group_id = message.chat.id
    if not kws:
        await message.reply('Usage: /add keyword1 keyword2')
        return
    tuples = [(k, 0) for k in kws]
    try:
        added = await models.add_keywords(group_id, message.from_user.id, tuples)
        await message.reply(f'Added {added} keywords.')
    except Exception as e:
        logger.exception('Error adding keywords: %s', e)
        await message.reply('Failed to add keywords due to an internal error.')


@router.message(Command('remove'))
async def cmd_remove(message: Message):
    if message.chat.type in ('private',):
        await message.reply('Please run /remove inside the group.')
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply('Usage: /remove keyword')
        return
    keyword = parts[1].strip()
    try:
        cnt = await models.remove_keyword(message.chat.id, message.from_user.id, keyword)
        await message.reply(f'Removed {cnt} entries for "{keyword}"')
    except Exception:
        logger.exception('Error removing keyword')
        await message.reply('Internal error')


@router.message(Command('list'))
async def cmd_list(message: Message):
    try:
        rows = await models.list_keywords_for_user(message.from_user.id)
        if not rows:
            await message.reply('You have no keywords configured.')
            return
        text_lines = []
        current_group = None
        for r in rows:
            gid, kw, regex_mode, created = r
            text_lines.append(f'Group {gid}: {kw} (regex={regex_mode})')
        await message.reply('\n'.join(text_lines))
    except Exception:
        logger.exception('Error listing keywords')
        await message.reply('Internal error')


@router.message(Command('clear'))
async def cmd_clear(message: Message):
    if message.chat.type in ('private',):
        await message.reply('Please run /clear inside the group.')
        return
    try:
        cnt = await models.clear_keywords(message.chat.id, message.from_user.id)
        await message.reply(f'Cleared {cnt} keywords for this group.')
    except Exception:
        logger.exception('Error clearing keywords')
        await message.reply('Internal error')
