import asyncio


from bot import bot, dp
from handlers import register_all_handlers
from utils.logger import get_bot_logger, setup_logger

from database import db
from google_sheets.api import cache_manager


async def on_startup():
    setup_logger()
    await db.create_tables()
    await cache_manager.initialize_cache()
    asyncio.create_task(cache_manager.auto_update_cache())
    
    register_all_handlers(dp)

    get_bot_logger().info('Бот начал свою работу')


async def on_shutdown():
    get_bot_logger().info('Бот завершил свою работу')


async def main():
    
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())