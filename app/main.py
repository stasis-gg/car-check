import asyncio
import logging
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import MenuButtonWebApp, WebAppInfo

from app.config import settings
from app.bot.handlers import router as bot_router
from app.webapp.routes import router as webapp_router

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("CarCheck")

# FastAPI App for Mini App & API
app = FastAPI(title="CarCheck Mini App API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webapp_router)

# Aiogram Bot & Dispatcher
bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.include_router(bot_router)

async def start_bot():
    logger.info("Запуск Telegram бота CarCheck...")
    while True:
        bot_instance = None
        try:
            bot_instance = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
            
            # Сбрасываем старые вебхуки и накопившиеся апдейты
            await bot_instance.delete_webhook(drop_pending_updates=True)

            # Устанавливаем кнопку меню WebApp в чате бота
            if settings.WEBAPP_URL and settings.WEBAPP_URL.startswith("https://"):
                try:
                    await bot_instance.set_chat_menu_button(
                        menu_button=MenuButtonWebApp(
                            text="🚗 Mini App",
                            web_app=WebAppInfo(url=settings.WEBAPP_URL)
                        )
                    )
                    logger.info(f"Кнопка MenuButtonWebApp настроена на {settings.WEBAPP_URL}")
                except Exception as ex:
                    logger.warning(f"Не удалось установить MenuButton: {ex}")

            logger.info("Aiogram polling успешно запущен...")
            await dp.start_polling(bot_instance, handle_signals=False)
        except Exception as e:
            logger.error(f"Сбой polling бота: {e}. Переподключение через 3 секунды...")
            await asyncio.sleep(3)
        finally:
            if bot_instance:
                try:
                    await bot_instance.session.close()
                except Exception:
                    pass


async def start_web():
    logger.info(f"Запуск веб-сервера Mini App на http://{settings.WEBAPP_HOST}:{settings.WEBAPP_PORT}...")
    config = uvicorn.Config(
        app=app,
        host=settings.WEBAPP_HOST,
        port=settings.WEBAPP_PORT,
        log_level="info",
        access_log=False
    )
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    logger.info("Запуск CarCheck сервиса (Бот + Mini App)...")
    await asyncio.gather(
        start_web(),
        start_bot()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Остановка приложения...")
