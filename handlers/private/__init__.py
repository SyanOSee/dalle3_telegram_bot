# Third-party
from aiogram import Router

# Routers
from .basic import basic_router
from .dalle import dalle_router
from .settings import settings_router

private_router = Router()
sub_routers = [
    basic_router, dalle_router, settings_router
]

private_router.include_routers(*sub_routers)
