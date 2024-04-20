# Third-party
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

# Project
import config as cf
from database import db, UserModel
from logger import bot_logger
from resources import strs

# __router__ !DO NOT DELETE!
basic_router = Router()


# __states__ !DO NOT DELETE!


# __buttons__ !DO NOT DELETE!


# __chat__ !DO NOT DELETE!
@basic_router.message(Command('start'))
async def handle_start_command(message: Message, state: FSMContext):
    """
    Handle the /start command from the user.

    Args:
        message (Message): The message object sent by the user.
        state (FSMContext): The state context.
    """
    bot_logger.info(f'Handling command /start from user {message.chat.id}')

    user = await db.users.get_by_id(user_id=message.chat.id)
    if not user:
        await db.users.insert(user=UserModel.create(user_id=message.chat.id, name=message.from_user.full_name))

    await message.answer(text=strs.start_msg)


@basic_router.message(Command('help'))
async def handle_help_command(message: Message, state: FSMContext):
    """
    Handle the /help command from the user.

    Args:
        message (Message): The message object sent by the user.
        state (FSMContext): The state context.
    """
    bot_logger.info(f'Handling command /help from user {message.chat.id}')
    await message.answer(text=strs.help_msg)
