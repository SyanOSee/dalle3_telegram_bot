# Importing necessary modules and classes from the package
from .private import private_router

# Contains all the routers available in the package for external access
all_routers = [private_router]

# List of classes, methods and modules that will be accessible when importing the package
__all__ = ['all_routers']