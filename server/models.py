# Third-party
from sqladmin import ModelView

# Project
from database import UserModel, SettingsModel


class UserView(ModelView, model=UserModel):
    """
    View class for User model.

    Attributes:
    name (str): Name of the view ('Пользователь').
    name_plural (str): Plural name of the view ('Пользователи').
    column_labels (dict): Mapping of model columns to labels.
    column_list (list): List of columns to display in the view.
    column_sortable_list (list): List of sortable columns.
    column_searchable_list (list): List of searchable columns.

    Methods:
    - __init__
    """
    name = 'Пользователь'
    name_plural = 'Пользователи'
    column_labels = {
        UserModel.user_id: 'ID пользователя',
        UserModel.name: 'Имя',
        UserModel.joined_date: 'Дата присоединения',
        UserModel.settings: 'Настройки'
    }
    column_list = [
        UserModel.user_id,
        UserModel.name,
        UserModel.joined_date,
    ]
    column_sortable_list = column_list
    column_searchable_list = [
        UserModel.user_id,
        UserModel.name,
    ]


class SettingsView(ModelView, model=SettingsModel):
    """
    View class for Settings model.

    Attributes:
    name (str): Name of the view ('Настройка').
    name_plural (str): Plural name of the view ('Настройки').
    column_labels (dict): Mapping of model columns to labels.
    column_list (list): List of columns to display in the view.
    column_sortable_list (list): List of sortable columns.
    column_searchable_list (list): List of searchable columns.

    Methods:
    - __init__
    """
    name = 'Настройка'
    name_plural = 'Настройки'
    column_labels = {
        SettingsModel.user_id: 'ID пользователя',
        SettingsModel.model: 'Модель',
        SettingsModel.size: 'Размер',
        SettingsModel.quantity: 'Количество',
    }
    column_list = [
        SettingsModel.user_id,
        SettingsModel.model,
        SettingsModel.size,
        SettingsModel.quantity,
    ]
    column_sortable_list = column_list
    column_searchable_list = [
        SettingsModel.model,
        SettingsModel.size,
    ]
