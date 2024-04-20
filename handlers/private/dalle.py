# Third-party
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InputMediaPhoto

# Project
from database import db, SettingsModel
from logger import bot_logger
from resources import strs
from gpt import send_dalle

# __router__ !DO NOT DELETE!
dalle_router = Router()


# __states__ !DO NOT DELETE!
class PromptState(StatesGroup):
    """
    Represents states involved in the image generation process using prompts.
    """
    get_prompt = State()


# __buttons__ !DO NOT DELETE!
async def get_decline_keyboard() -> ReplyKeyboardMarkup:
    """
    Generates a reply keyboard markup with a decline button.

    :return: An instance of ReplyKeyboardMarkup with a configured decline button.
    """
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Отмена ❌')]
    ], resize_keyboard=True)


@dalle_router.message(F.text == 'Отмена ❌')
async def handle_decline_message(message: Message, state: FSMContext):
    """
    Handles the decline action by the user, clearing the current state.

    :param message: The Message object from Telegram.
    :param state: The FSM context to clear the current user state.
    """
    bot_logger.info(f'Handling decline state from user {message.from_user.id}')
    await state.clear()
    await message.answer(
        text='<b>Команда отменена!</b>\n\nВоспользуйтесь командой <i>/help</i> для дальнейших действий',
        reply_markup=ReplyKeyboardRemove())


async def get_generate_options_inline_keyboard() -> InlineKeyboardMarkup:
    """
    Creates an inline keyboard markup for generating images options.

    :return: An instance of InlineKeyboardMarkup with options related to image generation.
    """
    button_list = [
        [InlineKeyboardButton(text='Продолжить ✅', callback_data=f'generate_accept_btn')]
    ]

    @dalle_router.callback_query(F.data.startswith('generate_accept_btn'))
    async def handle_accept_button_callback(callback: CallbackQuery, state: FSMContext):
        """
        Processes the acceptance of image generation by the user.

        :param callback: CallbackQuery object representing the callback trigger.
        :param state: FSM context for managing user states.
        """
        bot_logger.info(f'Handling generate_options accept button callback from user {callback.message.chat.id}')
        await callback.message.answer(text=strs.send_prompt_msg, reply_markup=await get_decline_keyboard())
        await state.set_state(PromptState.get_prompt.state)
        await callback.message.edit_text(text=callback.message.html_text, reply_markup=None)
        await callback.answer()

    return InlineKeyboardMarkup(inline_keyboard=button_list)


# __chat__ !DO NOT DELETE!
async def _make_up_user_status_msg(settings: SettingsModel) -> str:
    """
    Composes a user-specific status message showcasing their settings.

    :param settings: The settings model associated with a user.
    :return: A string formatted with the user's current image generation settings.
    """
    return (f'<b>Модель:</b> {settings.model}\n'
            f'<b>Размер изображения:</b> {settings.size}\n'
            f'<b>Количество:</b> {settings.quantity}\n\n'
            f'Изменить настройки: <i>/settings</i>')


@dalle_router.message(Command('generate'))
async def handle_generate_command(message: Message, state: FSMContext):
    """
    Triggered by the /generate command, initiating the image generation process.

    :param message: Telegram message triggering this handler.
    :param state: The FSM context for managing user states.
    """
    bot_logger.info(f'Handling command /generate from user {message.chat.id}')

    user = await db.users.get_by_id(user_id=message.chat.id)
    if not user:
        await message.answer(text=strs.inner_error_msg)
        return
    await message.answer(
        text=await _make_up_user_status_msg(settings=user.settings),
        reply_markup=await get_generate_options_inline_keyboard()
    )


@dalle_router.message(PromptState.get_prompt)
async def handle_get_prompt_state(message: Message, state: FSMContext):
    """
    Handles the user's prompt input for image generation.

    :param message: The user's prompt message.
    :param state: FSM context to manage state transitions and data.
    """
    bot_logger.info(f'Handling states PromptState.get_prompt from user {message.chat.id}')
    prompt = message.text
    if prompt:
        await state.clear()
        wait_msg = await message.answer(text=strs.generating_msg, reply_markup=ReplyKeyboardRemove())
        await process_prompt_input(message, wait_msg, prompt)
    else:
        await message.answer(text=strs.send_prompt_error_msg)
        return


async def process_prompt_input(message: Message, wait_msg: Message, prompt: str):
    """
    Process the prompt input from the user, generate images, and send them to the user.

    :param message: Telegram message received from the user.
    :param wait_msg: Wait message displayed to the user while processing.
    :param prompt: Prompt text to generate images from.
    """
    user = await db.users.get_by_id(user_id=message.chat.id)
    response = await send_dalle(
        prompt=prompt, size=user.settings.size,
        model=user.settings.model, quantity=user.settings.quantity
    )
    await send_generated_images(message, response)
    await wait_msg.delete()


async def send_generated_images(message: Message, response: dict):
    """
    Send generated images to the user based on the response data received.

    :param message: Telegram message object.
    :param response: Dictionary containing the response data from image generation.
    """
    image_list = response['data']
    try:
        if len(image_list) > 1:
            await send_image_group(message, image_list)
        else:
            await send_single_image(message, response['data'][0].get('url', ''))
    except Exception as e:
        bot_logger.error(e)
        await message.answer(text=strs.inner_error_msg)


async def send_image_group(message: Message, image_list: list):
    """
    Send a group of generated images in a media group to the user.

    :param message: Telegram message object.
    :param image_list: List of images to be sent in a group.
    """
    media_group = [InputMediaPhoto(media=image.get('url', '')) for image in image_list]
    await message.bot.send_media_group(
        chat_id=message.chat.id,
        media=media_group,
    )


async def send_single_image(message: Message, image_url: str):
    """
    Send a single generated image to the user.

    :param message: Telegram message object.
    :param image_url: URL of the image to be sent.
    """
    await message.bot.send_photo(
        chat_id=message.chat.id,
        photo=image_url
    )
