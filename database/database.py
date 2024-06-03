# Third-party
import sqlalchemy.exc
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, joinedload

# Standard
from time import sleep
import traceback
from enum import Enum

# Project
import config as cf
from logger import database_logger
from .models import base, UserModel, SettingsModel


# Enum for different types of database connections
class Type(Enum):
    POSTGRESQL = f'postgresql+psycopg2://{cf.database["user"]}:{cf.database["password"]}@{cf.database["host"]}:{cf.database["port"]}'
    SQLITE = f'sqlite:///{cf.SQLITE_PATH}'


class Database:
    """
    A class to interact with the database.

    Attributes:
    type_ (Type): The type of database connection.
    """

    # Private method to connect to the database
    def __connect_to_database(self, type_: Type):
        """
        Connect to the database using the specified type.

        Args:
        type_ (Type): The type of database connection.
        """
        while True:
            database_logger.warning('Connecting to database...')
            try:
                # Creating a database engine
                self.engine = create_engine(type_.value)
                self.session_maker = sessionmaker(bind=self.engine)
                # Creating tables defined in 'base' metadata
                base.metadata.create_all(self.engine)

                # __connect_inner_classes__ !DO NOT DELETE!

                self.users = self.User(session_maker=self.session_maker)
                self.settings = self.Settings(session_maker=self.session_maker)

                database_logger.info('Connected to database')
                break
            except sqlalchemy.exc.OperationalError:
                # Handling database connection errors
                database_logger.error('Database error:\n' + traceback.format_exc())
                sleep(5.0)

    # Constructor to initialize the Database class
    def __init__(self, type_: Type):
        """
        Initialize the Database class with the specified type.

        Args:
        type_ (Type): The type of database connection.
        """
        self.__connect_to_database(type_=type_)

    # __inner_classes__ !DO NOT DELETE!
    class User:
        """
        A class to handle user-related database operations.
        """

        def __init__(self, session_maker):
            """
            Initialize the User class with the session maker.

            Args:
            session_maker: The session maker object.
            """
            self.session_maker = session_maker

        async def insert(self, user: UserModel):
            """
            Insert a new user into the database.

            Args:
            user (UserModel): The user object to insert.
            """
            with self.session_maker() as session:
                session.add(user)
                session.commit()
                database_logger.info(f'UserModel is created!')
                session.close()

        async def get_all(self) -> list[UserModel] | None:
            """
            Get all user models from the database.

            Returns:
            list[UserModel] | None: A list of user models or None if no users found.
            """
            with self.session_maker() as session:
                data = session.query(UserModel).all()
                if data:
                    database_logger.info('Fetched all UserModels')
                    return data
                else:
                    database_logger.info('No UserModels in the database')
                    return None

        async def get_by_id(self, user_id: int) -> UserModel | None:
            """
            Get a user model by user ID from the database.

            Args:
            user_id (int): The user ID to retrieve.

            Returns:
            UserModel | None: The user model or None if not found.
            """
            with self.session_maker() as session:
                data = session.query(UserModel).options(joinedload(UserModel.settings)).filter_by(
                    user_id=user_id).first()
                if data:
                    database_logger.info(f'UserModel {user_id} is retrieved from the database')
                    return data
                else:
                    database_logger.info(f'UserModel {user_id} is not in the database')
                    return None

        async def delete(self, user: UserModel):
            """
            Delete a user from the database.

            Args:
            user (UserModel): The user object to delete.
            """
            with self.session_maker() as session:
                session.query(UserModel).filter_by(user_id=user.user_id).delete()
                database_logger.warning(f'UserModel {user.user_id} is deleted!')
                session.commit()
                session.close()

        async def update(self, user: UserModel):
            """
            Update a user in the database.

            Args:
            user (UserModel): The user object to update.
            """
            with self.session_maker() as session:
                database_logger.warning(f'UserModel {user.user_id} is updated!')
                session.query(UserModel).filter_by(user_id=user.user_id).update({
                    key: getattr(user, key) for key in user.__dict__.keys()
                })
                session.commit()
                session.close()

    class Settings:
        """
        A class to handle settings-related database operations.
        """

        def __init__(self, session_maker):
            """
            Initialize the Settings class with the session maker.

            Args:
            session_maker: The session maker object.
            """
            self.session_maker = session_maker

        async def insert(self, settings: SettingsModel):
            """
            Insert settings into the database.

            Args:
            settings (SettingsModel): The settings object to insert.
            """
            with self.session_maker() as session:
                session.add(settings)
                session.commit()
                database_logger.info(f'Settings is created!')
                session.close()

        async def update(self, settings: SettingsModel):
            """
            Update settings in the database.

            Args:
            settings (SettingsModel): The settings object to update.
            """
            with self.session_maker() as session:
                database_logger.warning(f'Settings {settings.user_id} is updated!')

                # Specify the columns to update
                session.query(SettingsModel).filter_by(user_id=settings.user_id).update({
                    'model': settings.model,
                    'size': settings.size,
                    'quantity': settings.quantity,
                })

                session.commit()
                session.close()

        async def delete(self, settings: SettingsModel):
            """
            Delete settings from the database.

            Args:
            settings (SettingsModel): The settings object to delete.
            """
            with self.session_maker() as session:
                session.query(SettingsModel).filter_by(user_id=settings.user_id).delete()
                database_logger.warning(f'Settings {settings.user_id} is deleted!')
                session.commit()
                session.close()


# Create an instance of the Database class with a PostgreSQL connection
db = Database(type_=Type.SQLITE)