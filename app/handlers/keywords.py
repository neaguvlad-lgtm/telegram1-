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
    """Parse private chat arguments of the form: "Group Name" kw1 kw2
    Group name must be quoted. Keywords may be plain words or quoted strings.
    Returns (group_name, keywords) or (None, None).
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
    # Parse keywords robustly (allow quoted keywords as well)
    kws = _parse_keywords_from_rest(rest)
    return group, kws


def _parse_keywords_from_rest(rest: str):
    """Parse rest of the string into keywords, supporting quoted or unquoted tokens."""
    tokens = []
    i = 0
    while i < len(rest):
        if rest[i] == '"':
            j = rest.find('"', i+1)
            if j == -1:
                # unmatched quote, take the rest without quotes
                tokens.append(rest[i+1:])
                break
            tokens.append(rest[i+1:j])
            i = j + 1
            continue
        if rest[i].isspace():
            i += 1
            continue
        # unquoted token
        j = i
        while j < len(rest) and not rest[j].isspace():
            j += 1
        tokens.append(rest[i:j])
        i = j
    return tokens


@router.message(Command('add'))
async def cmd_add(message: Message):
    # Support adding from private: /add "Group Name" keyword1 keyword2 (or quoted keywords)
    if message.chat.type == 'private':
        rest = (message.text or '').strip()
        if rest.lower().startswith('/add'):
            rest = rest[len('/add'):].strip()
        if not rest:
            await message.reply('Usage in private: /add "Group Name" keyword1 keyword2')
            return
        group_name, kws = _parse_group_and_keywords(rest)
        if not group_name or not kws:
            await message.reply('Invalid format. Use: /add "Group Name" keyword1 keyword2')
            return
        # find group id by title (case-insensitive, with fallback)
        found = await models.find_group_by_title(group_name)
        if not found:
            await message.reply(
                f'Group with title "{group_name}" not found. \n'
                'Tip: The bot can only manage keywords for a group after it has seen at least one message in that group (privacy mode must be disabled). \n'
                'Please go to that group, send a message, and then try /add again.'
            )
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
        # Build grouped view with titles when available
        text_lines = []
        for r in rows:
            gid, kw, regex_mode, created = r
            try:
                title = await models.get_group_title(gid)
            except Exception:
                title = None
            display = f"Group {title or gid}: {kw} (regex={regex_mode})"
            text_lines.append(display)
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


@router.message(Command('known_groups'))
async def cmd_known_groups(message: Message):
    # Private chat only; help user know which groups titles are known
    if message.chat.type != 'private':
        await message.reply('Please use this command in a private chat with the bot.')
        return
    try:
        groups = await models.list_user_groups(message.from_user.id)
        if not groups:
            await message.reply('No known groups found for your account.')
            return
        lines = []
        for gid, title in groups:
            if title:
                lines.append(f'Group: {title} (id: {gid})')
            else:
                lines.append(f'Group id: {gid}')
        await message.reply('\n'.join(lines))
    except Exception:
        logger.exception('Error listing known groups')
        await message.reply('Internal error')
