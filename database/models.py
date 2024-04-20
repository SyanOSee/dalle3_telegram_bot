# Third-party
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Project
from gpt import Model, Size

# Creating a base class for declarative models
base = declarative_base()


class UserModel(base):
    """
    Represents a user in the database.

    Attributes:
    user_id (BigInteger): The unique identifier for the user.
    name (String): The name of the user.
    joined_date (DateTime): The date the user joined.
    settings (Relationship): The settings associated with the user.
    """

    __tablename__ = 'Users'
    user_id = Column(BigInteger, primary_key=True)
    name = Column(String)
    joined_date = Column(DateTime, default=func.now())

    # Relationship with Settings table
    settings = relationship('SettingsModel', uselist=False, back_populates='user')

    @staticmethod
    def create(user_id: int, name: str):
        """
        Creates a new user with the given user ID and name.

        Args:
        user_id (int): The user ID.
        name (str): The name of the user.

        Returns:
        UserModel: The created user.
        """
        user = UserModel(
            user_id=user_id,
            name=name,
        )
        settings = SettingsModel.create(user_id=user_id)
        user.settings = settings

        return user


class SettingsModel(base):
    """
    Represents settings for a user.

    Attributes:
    id (BigInteger): The unique identifier for the settings.
    model (String): The model to use.
    size (String): The size of the model.
    quantity (int): The quantity of settings.
    user_id (BigInteger): The user ID associated with the settings.
    user (Relationship): The user associated with the settings.
    """

    __tablename__ = 'Settings'
    id = Column(BigInteger, primary_key=True)
    model = Column(String, default=Model.DALLE_2.value)
    size = Column(String, default=Size.S_256.value)
    quantity = Column(Integer, default=1)

    user_id = Column(BigInteger, ForeignKey('Users.user_id'))
    user = relationship('UserModel', back_populates='settings')

    @staticmethod
    def create(user_id: int, model=Model.DALLE_2.value, size=Size.S_256.value, quantity=1):
        """
        Creates settings for a user with the given parameters.

        Args:
        user_id (int): The user ID.
        model (str): The model to use.
        size (str): The size of the model.
        quantity (int): The quantity of settings.

        Returns:
        SettingsModel: The created settings.
        """
        return SettingsModel(
            user_id=user_id,
            model=model,
            size=size,
            quantity=quantity,
        )
