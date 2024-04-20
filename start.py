# Third-party
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Standard
import asyncio

# Project
from bot import bot, dispatcher
from handlers import all_routers
from logger import bot_logger
from server import start_panel

dispatcher.include_routers(*all_routers)


async def start_bot():
    """
    Start the bot and configure polling with allowed updates.
    """
    await bot.delete_webhook(drop_pending_updates=True)

    bot_logger.info('Bot started!')
    await dispatcher.start_polling(
        bot,
        allowed_updates=[
            'message', 'callback_query'
        ]  # Add needed router updates
    )


async def run_app():
    """
    Run the bot application by starting the bot and the panel.
    """
    await asyncio.gather(
        start_bot(),
        start_panel()
    )


if __name__ == '__main__':
    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_app)
    scheduler.start()
    asyncio.get_event_loop().run_forever()
