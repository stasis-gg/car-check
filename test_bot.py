import asyncio
import sys
import logging

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from app.main import bot, dp, app, settings

async def test_bot():
    print("Testing get_me()...")
    me = await bot.get_me()
    print(f"Bot info: @{me.username} ({me.first_name})")

    print("Testing delete_webhook()...")
    await bot.delete_webhook(drop_pending_updates=True)

    print("Testing set_chat_menu_button()...")
    if settings.WEBAPP_URL and settings.WEBAPP_URL.startswith("https://"):
        from aiogram.types import MenuButtonWebApp, WebAppInfo
        try:
            await bot.set_chat_menu_button(
                menu_button=MenuButtonWebApp(
                    text="🚗 Mini App",
                    web_app=WebAppInfo(url=settings.WEBAPP_URL)
                )
            )
            print("Menu button set successfully!")
        except Exception as e:
            print("Menu button error:", e)

    await bot.session.close()
    print("Bot test passed without errors.")

if __name__ == "__main__":
    asyncio.run(test_bot())
