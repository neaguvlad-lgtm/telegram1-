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
        '   (e.g. /add "Group Name" keyword)\n'
        '/remove keyword - remove a keyword for a group or the current group for the user (private)\n'
        '/list - list your keywords (group and keyword view)\n'
        '/clear - clear all keywords for a group for this user\n'
        '/known_groups - list groups you have configured keywords for (private chat)\n'
        'Notes:\n'
        '- Ensure the bot is in the group and privacy mode is disabled (BotFather /setprivacy)\n'
        '- Titles are matched with a forgiving approach (private /known_groups helps)\n'
    )
    await message.answer(text)
