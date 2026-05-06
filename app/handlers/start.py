from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command('start'))
async def cmd_start(message: Message):
    text = (
        'Welcome to Keyword Forwarder Bot!\n'
        'Add keywords in a group with:\n'
        '/add keyword1 keyword2\n'
        'Remove with: /remove keyword\n'
        '/list to list your keywords\n'
        '/clear to clear your keywords for this group\n'
        'Use /help for more details.'
    )
    await message.answer(text)


@router.message(Command('help'))
async def cmd_help(message: Message):
    text = (
        'Commands:\n'
        '/add "Group Name" keyword1 keyword2 - add keywords for a group from private chat.\n'
        '   (e.g. /add "Zeus" buna)\n'
        '/remove keyword - remove a keyword for current group and user\n'
        '/list - list your keywords (incl. group titles if available)\n'
        '/clear - clear all keywords for current group for this user\n'
        '/known_groups - list groups you have configured keywords for (private chat)\n'
        'Notes:\n'
        '- Ensure the bot is in the group and privacy mode is disabled (BotFather /setprivacy)\n'
        '- Your group title must match exactly (case-insensitive fallback is supported)\n'
    )
    await message.answer(text)
