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
        '/add keyword1 keyword2 - add multiple keywords for this group\n'
        '/remove keyword - remove a keyword\n'
        '/list - list your keywords across groups\n'
        '/clear - clear all your keywords for this group\n'
        'Notes:\n'
        '- Run these commands inside the group where you want keywords to apply.\n'
        '- Disable privacy mode via BotFather to let bot see all messages.\n'
    )
    await message.answer(text)
