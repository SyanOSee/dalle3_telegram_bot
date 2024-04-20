# Importing necessary modules and classes from the package
from .database import db
from .models import UserModel, SettingsModel

# List of classes and modules that will be accessible when importing the package
__all__ = ['UserModel', 'SettingsModel', 'db']
