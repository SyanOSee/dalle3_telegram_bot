# Third-party
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message, CallbackQuery

# Project
from database import db, UserModel
from logger import bot_logger
from resources import strs
from gpt import Model, Size

# Standard
from enum import Enum

# __router__ !DO NOT DELETE!
settings_router = Router()


# __states__ !DO NOT DELETE!


# __buttons__ !DO NOT DELETE!
@settings_router.callback_query(F.data.startswith('close'))
async def handle_close_button_callback(callback: CallbackQuery, state: FSMContext):
    """
    Handles the close button callback from the user, deleting the message and answering the callback.

    :param callback: The CallbackQuery object from Telegram.
    :param state: The FSM context to manage the state of the conversation.
    """
    bot_logger.info(f'Handling close callback from user {callback.message.chat.id}')
    await callback.message.delete()
    await callback.answer()


class BackRoutes(Enum):
    """
    An enumeration class to define the back routes for different resources.

    Enum Values:
        MODEL: Represents the route for models.
        SIZE: Represents the route for sizes.
    """
    MODEL = 'models'
    SIZE = 'sizes'


async def _check_user_exists(callback: CallbackQuery) -> UserModel | None:
    """
    Checks if the user exists in the database.

    :param callback: The CallbackQuery object from Telegram.

    :return: The user object if exists, None otherwise.
    """
    user = await db.users.get_by_id(user_id=callback.message.chat.id)
    if not user:
        await callback.answer(text=strs.inner_error_msg, show_alert=True)
        return
    return user


async def _update_user_settings(callback: CallbackQuery, key: str, value: any) -> UserModel | None:
    """
    Updates the user settings in the database.

    :param callback: The CallbackQuery object from Telegram.
    :param key: The key to update in the user settings.
    :param value: The new value to set for the key.

    :return: The updated user object if successful, None otherwise.
    """
    user = await _check_user_exists(callback=callback)

    setattr(user.settings, key, value)
    await db.settings.update(user.settings)

    return user


async def _create_button_list(
        items: list[any], user_settings_value: any,
        callback_prefix: str, max_items_per_row: int
) -> list:
    """
    Creates a list of inline buttons for the user settings.

    :param items: The list of items to create buttons for.
    :param user_settings_value: The current value of the user setting.
    :param callback_prefix: The prefix for the callback data.
    :param max_items_per_row: The maximum number of items per row for buttons.

    :return: The list of inline buttons.
    """
    button_list = []
    row = []
    for item in items:
        if len(row) == max_items_per_row:
            button_list.append(row)
            row = []
        if isinstance(item, Enum):
            text = item.value if item.value != user_settings_value else item.value + ' ' + '✔️'
            callback_data = item.value
        else:
            text = item if item != user_settings_value else item + ' ' + '✔️'
            callback_data = item
        row.append(InlineKeyboardButton(text=text, callback_data=f'{callback_prefix} {callback_data}'))
    button_list.append(row)
    return button_list


async def _get_back_close_buttons(back_to: BackRoutes | None = None, show_back_to: bool = True) -> list:
    """
    Gets the back and close inline buttons.

    :param back_to: The route to go back to.
    :param show_back_to: Boolean value to indicate whether to show the back button or not.
    :return: The list of back and close inline buttons.
    """
    button_list = [[InlineKeyboardButton(text='Закрыть ❌', callback_data='close')]]
    if show_back_to:
        button_list.insert(0, [InlineKeyboardButton(text='⬅️ Назад', callback_data=f'back_to {back_to.value}')])
    return button_list


@settings_router.callback_query(F.data.startswith('back_to'))
async def handle_back_to_button_callback(callback: CallbackQuery, state: FSMContext):
    """
    Handle back_to button callbacks to go back to previous settings.

    :param callback: The Callback Query object.
    :param state: The FSM Context.
    """
    bot_logger.info(f'Handling back_to callback from user {callback.message.chat.id}')
    data = callback.data.split()
    route = data[1]

    user = await _check_user_exists(callback=callback)

    text, keyboard = '', None
    match route:
        case BackRoutes.MODEL.value:
            text, keyboard = strs.choose_model_msg, await get_choose_model_inline_keyboard(user=user)
        case BackRoutes.SIZE.value:
            text, keyboard = strs.choose_size_msg, await get_choose_size_inline_keyboard(
                user=user, model=user.settings.model
            )

    await callback.message.edit_text(text=text, reply_markup=keyboard)
    await callback.answer()


async def get_choose_quantity_keyboard(user: UserModel) -> InlineKeyboardMarkup:
    """
    Get the inline keyboard for choosing quantity.

    :param user: The User Model object.

    :return: The Inline Keyboard Markup.
    """
    nums = {
        1: '1️⃣', 2: '2️⃣', 3: '3️⃣', 4: '4️⃣', 5: '5️⃣', 6: '6️⃣'
    }
    button_list = await _create_button_list(
        items=[nums[i] for i in range(1, 6 + 1)], user_settings_value=nums[user.settings.quantity],
        callback_prefix='choose_quantity', max_items_per_row=3
    )
    button_list += await _get_back_close_buttons(back_to=BackRoutes.SIZE)

    @settings_router.callback_query(F.data.startswith('choose_quantity'))
    async def handle_choose_quantity_button_callback(callback: CallbackQuery, state: FSMContext):
        """
        Handle choose quantity button callbacks.

        :param callback: The Callback Query object.
        :param state: The FSM Context.
        """
        bot_logger.info(f'Handling choose_quantity a button callback from user {callback.message.chat.id}')
        data = callback.data.split()
        quantity = [key for key in nums.keys() if nums[key] == data[1]][0]

        user = await _update_user_settings(callback=callback, key='quantity', value=quantity)

        await callback.message.edit_text(
            text=strs.choose_model_msg,
            reply_markup=await get_choose_model_inline_keyboard(user=user)
        )

        await callback.answer()

    return InlineKeyboardMarkup(inline_keyboard=button_list)


async def get_choose_size_inline_keyboard(user: UserModel, model: str) -> InlineKeyboardMarkup:
    """
      Get the inline keyboard for choosing size.

      :param user: The User Model object.
      :param model: The selected model.

      :return: The Inline Keyboard Markup.
      """
    sizes = [Size.S_256, Size.S_512, Size.S_1024]
    if model == Model.DALLE_3.value:
        sizes = [Size.S_1024, Size.S_1024_x_1792, Size.S_1792_x_1024]

    button_list = await _create_button_list(
        items=sizes, user_settings_value=user.settings.size,
        callback_prefix='choose_size', max_items_per_row=3
    )
    button_list += await _get_back_close_buttons(back_to=BackRoutes.MODEL)

    @settings_router.callback_query(F.data.startswith('choose_size'))
    async def handle_choose_size_button_callback(callback: CallbackQuery, state: FSMContext):
        """
          Handle choose size button callbacks.

          :param callback: The Callback Query object.
          :param state: The FSM Context.
        """
        bot_logger.info(f'Handling choose_size a button callback from user {callback.message.chat.id}')
        data = callback.data.split()
        size = data[1]

        user = await _update_user_settings(callback=callback, key='size', value=size)

        await callback.message.edit_text(
            text=strs.choose_quantity_msg,
            reply_markup=await get_choose_quantity_keyboard(user=user))
        await callback.answer()

    return InlineKeyboardMarkup(inline_keyboard=button_list)


async def get_choose_model_inline_keyboard(user: UserModel) -> InlineKeyboardMarkup:
    """
    Get the inline keyboard for choosing model.

    :param user: The User Model object.

    :return: The Inline Keyboard Markup.
    """
    models = [model.value for model in Model]
    button_list = await _create_button_list(
        items=models, user_settings_value=user.settings.model,
        callback_prefix='choose_model', max_items_per_row=2
    )
    button_list += await _get_back_close_buttons(show_back_to=False)

    @settings_router.callback_query(F.data.startswith('choose_model'))
    async def handle_model_button_callback(callback: CallbackQuery, state: FSMContext):
        """
        Handle choose model button callbacks.

        :param callback: The Callback Query object.
        :param state: The FSM Context.
        """
        bot_logger.info(f'Handling choose_model model button callback from user {callback.message.chat.id}')
        data = callback.data.split()
        model = data[1]

        user = await _update_user_settings(callback=callback, key='model', value=model)

        await callback.message.edit_text(
            text=strs.choose_size_msg,
            reply_markup=await get_choose_size_inline_keyboard(
                user=user, model=user.settings.model
            ))
        await callback.answer()

    return InlineKeyboardMarkup(inline_keyboard=button_list)


# __chat__ !DO NOT DELETE!
@settings_router.message(Command('settings'))
async def handle_settings_command(message: Message, state: FSMContext):
    """
       Handle the /settings command to start user settings.

       :param message: The Message object.
       :param state: The FSM Context.
       """
    bot_logger.info(f'Handling command /settings from user {message.chat.id}')

    user = await db.users.get_by_id(user_id=message.chat.id)
    if not user:
        await message.answer(text=strs.inner_error_msg)
        return

    await message.answer(
        text=strs.choose_model_msg,
        reply_markup=await get_choose_model_inline_keyboard(
            user=user
        )
    )
