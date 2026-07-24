# =====================================================================================##
#
#  ██╗░░██╗███╗░░██╗██████╗░░█████╗░████████╗███████╗██████╗░
#  ██║░░██║████╗░██║██╔══██╗██╔══██╗╚══██╔══╝██╔════╝██╔══██╗
#  ██║░░██║██╔██╗██║██████╔╝███████║░░░██║░░░█████╗░░██║░░██║
#  ██║░░██║██║╚████║██╔══██╗██╔══██║░░░██║░░░██╔══╝░░██║░░██║
#  ╚██████╔╝██║░╚███║██║░░██║██║░░██║░░░██║░░░███████╗██████╔╝
#  ░╚═════╝░╚═╝░░╚══╝╚═╝░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░╚══════╝╚═════╝░
#
#  ░██████╗░██████╗░██████╗░███████╗██████╗░
#  ██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗
#  ██║░░░░░██║░░░██║██║░░██║█████╗░░██████╔╝
#  ██║░░░░░██║░░░██║██║░░██║██╔══╝░░██╔══██╗
#  ╚██████╗╚██████╔╝██████╔╝███████╗██║░░██║
#  ░╚═════╝░╚═════╝░╚═════╝░╚══════╝╚═╝░░╚═╝
#
#                         ✨ MADE BY UNRATED CODER ✨
#                  Join Updates Channel: https://t.me/UNRATED_CODER
#=====================================================================================##

import asyncio
import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, OWNER_ID, API_ID, API_HASH
from plugins import all_routers
from plugins.login import cleanup_all_listeners

logger = logging.getLogger("TGStorageBot.bot")

# Initialize Bot & Dispatcher
if not BOT_TOKEN or ":" not in BOT_TOKEN:
    bot = Bot(token="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")
else:
    bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Register all plugins command routers
for router in all_routers:
    dp.include_router(router)

async def handle_health_check(reader, writer):
    try:
        await reader.read(1024)
        response = "HTTP/1.1 200 OK\r\nContent-Length: 2\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\nOK"
        writer.write(response.encode('utf-8'))
        await writer.drain()
    except Exception as e:
        logger.error(f"Error handling health check request: {e}")
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except:
            pass

async def start_health_check_server():
    port = int(os.getenv("PORT", "8080"))
    logger.info(f"Starting lightweight health check server on port {port}...")
    try:
        server = await asyncio.start_server(handle_health_check, "0.0.0.0", port)
        return server
    except Exception as e:
        logger.error(f"Failed to start health check server on port {port}: {e}")
        return None

# Send notification to Owner on startup
async def notify_owner_on_startup():
    if OWNER_ID:
        try:
            logger.info(f"Sending restart notification to owner (ID: {OWNER_ID})...")
            await bot.send_message(chat_id=OWNER_ID, text="bot restarted by @Unrated_Coder")
        except Exception as e:
            logger.warning(f"Could not send startup notification to owner: {e}")

# Main launch logic
async def main():
    logger.info("Starting Telegram ID Storage Bot...")
    if not BOT_TOKEN:
        logger.critical("BOT_TOKEN environment variable is not defined!")
        return
    if API_ID == 0 or not API_HASH:
        logger.warning("API_ID or API_HASH fallback credentials are not set. Add_account login will fail.")

    # Start health check server in background
    health_server = await start_health_check_server()

    # Send restart message to owner
    await notify_owner_on_startup()

    # Remove Webhook and Start Polling
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    finally:
        # Clean up health check server if it was started
        if health_server:
            health_server.close()
            await health_server.wait_closed()
            logger.info("Health check server shut down.")

        # Ensure cleanup of any active listeners
        await cleanup_all_listeners()

if __name__ == "__main__":
    asyncio.run(main())
