# =====================================================================================##
#
#  ██╗░░██╗███╗░░██╗██████╗░░█████╗░████████╗███████╗██████╗░
#  ██║░░██║████╗░██║██╔══██╗██╔══██╗╚══██╔══╝██╔════╝██╔══██╗
#  ██║░░██║██╔██╗██║██████╔╝███████║░░░██║░░░█████╗░░██║░░██║
#  ██║░░██║██║╚████║██╔══██╗██╔══██║░░░██║░░░██╔══╝░░██║░░██║
#  ╚█████╔╝██║░╚███║██║░░██║██║░░██║░░░██║░░░███████╗██████╔╝
#  ░╚════╝░╚═╝░░╚══╝╚═╝░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░╚══════╝╚═════╝░
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

import re
import html
import asyncio
import logging
from aiogram import Router, F, Bot, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

from database import get_account, get_all_accounts
from helpers import decrypt_data, create_pyrogram_client

logger = logging.getLogger("TGStorageBot.plugins.login")

router = Router()

# Active listeners for OTP retrieval: mapping of phone_number -> listener task / client info
# Each item has: {"client": Client, "task": asyncio.Task, "admin_chat_id": int}
active_otp_listeners = {}

def get_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴍᴇɴᴜ", callback_data="menu:main")]
    ])

@router.callback_query(F.data == "menu:login")
async def start_login_callback(callback_query: CallbackQuery):
    await callback_query.answer()
    accounts = await get_all_accounts(user_id=callback_query.from_user.id)
    if not accounts:
        await callback_query.message.edit_text(
            "📭 <b>ɴᴏ sᴀᴠᴇᴅ ᴛᴇʟᴇɢʀᴀᴍ ᴀᴄᴄᴏᴜɴᴛs ꜰᴏᴜɴᴅ. ᴘʟᴇᴀsᴇ ᴀᴅᴅ ᴀɴ ᴀᴄᴄᴏᴜɴᴛ ꜰɪʀsᴛ.</b>",
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )
        return

    keyboard_builder = []
    for acc in accounts:
        phone = acc.get("phone")
        keyboard_builder.append([
            InlineKeyboardButton(text=f"🔑 ɢᴇᴛ ᴏᴛᴘ: {phone}", callback_data=f"retrieve_otp:{phone}")
        ])
    keyboard_builder.append([InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴍᴇɴᴜ", callback_data="menu:main")])

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard_builder)
    await callback_query.message.edit_text(
        "🔑 <b>sᴇʟᴇᴄᴛ ᴀɴ ᴀᴄᴄᴏᴜɴᴛ ᴛᴏ ᴛʀɪɢɢᴇʀ ʙᴀᴄᴋɢʀᴏᴜɴᴅ ʟᴏɢɪɴ ᴏᴛᴘ ᴄᴀᴘᴛᴜʀᴇ:</b>",
        reply_markup=markup,
        parse_mode="HTML"
    )

@router.message(Command("login"))
async def start_login_handler(message: Message):
    accounts = await get_all_accounts(user_id=message.from_user.id)
    if not accounts:
        await message.answer(
            "📭 <b>ɴᴏ sᴀᴠᴇᴅ ᴛᴇʟᴇɢʀᴀᴍ ᴀᴄᴄᴏᴜɴᴛs ꜰᴏᴜɴᴅ. ᴘʟᴇᴀsᴇ ᴀᴅᴅ ᴀɴ ᴀᴄᴄᴏᴜɴᴛ ꜰɪʀsᴛ.</b>",
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )
        return

    keyboard_builder = []
    for acc in accounts:
        phone = acc.get("phone")
        keyboard_builder.append([
            InlineKeyboardButton(text=f"🔑 ɢᴇᴛ ᴏᴛᴘ: {phone}", callback_data=f"retrieve_otp:{phone}")
        ])
    keyboard_builder.append([InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴍᴇɴᴜ", callback_data="menu:main")])

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard_builder)
    await message.answer(
        "🔑 <b>sᴇʟᴇᴄᴛ ᴀɴ ᴀᴄᴄᴏᴜɴᴛ ᴛᴏ ᴛʀɪɢɢᴇʀ ʙᴀᴄᴋɢʀᴏᴜɴᴅ ʟᴏɢɪɴ ᴏᴛᴘ ᴄᴀᴘᴛᴜʀᴇ:</b>",
        reply_markup=markup,
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("retrieve_otp:"))
async def process_otp_retrieve(callback_query: CallbackQuery, bot: Bot = None):
    phone = callback_query.data.split(":", 1)[1]
    admin_chat_id = callback_query.message.chat.id
    target_bot = bot or callback_query.bot
    await callback_query.answer()

    if phone in active_otp_listeners:
        await callback_query.message.edit_text(
            f"🔄 <b>ᴀʟʀᴇᴀᴅʏ ʟɪsᴛᴇɴɪɴɢ ꜰᴏʀ ʟᴏɢɪɴ ᴏᴛᴘs ᴏɴ</b> <code>{html.escape(phone)}</code>.\n\n"
            f"ʏᴏᴜ ᴄᴀɴ ʀᴇǫᴜᴇsᴛ ᴄᴏᴅᴇ ɴᴏᴡ ᴏɴ ʏᴏᴜʀ ɴᴇᴡ ᴅᴇᴠɪᴄᴇ.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⏹️ sᴛᴏᴘ ʟɪsᴛᴇɴɪɴɢ", callback_data=f"stop_listen:{phone}")],
                [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴍᴇɴᴜ", callback_data="menu:main")]
            ])
        )
        return

    acc = await get_account(phone, user_id=callback_query.from_user.id)
    if not acc:
        await callback_query.message.edit_text(
            "❌ <b>sᴇʟᴇᴄᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛ ɴᴏ ʟᴏɴɢᴇʀ ᴇxɪsᴛs ɪɴ ᴅᴀᴛᴀʙᴀsᴇ.</b>",
            reply_markup=get_back_keyboard(),
            parse_mode="HTML"
        )
        return

    encrypted_session = acc.get("encrypted_session")
    proxy = acc.get("proxy")
    custom_api = acc.get("custom_api")

    try:
        session_str = decrypt_data(encrypted_session)
    except Exception as e:
        logger.error(f"Failed to decrypt session: {e}")
        await callback_query.message.edit_text(
            "❌ <b>ᴅᴇᴄʀʏᴘᴛɪᴏɴ ᴇʀʀᴏʀ. ᴛʜᴇ ᴇɴᴄʀʏᴘᴛɪᴏɴ ᴋᴇʏ ᴍᴀʏ ʜᴀᴠᴇ ᴄʜᴀɴɢᴇᴅ.</b>",
            reply_markup=get_back_keyboard(),
            parse_mode="HTML"
        )
        return

    await callback_query.message.edit_text(
        f"⏳ <b>ᴀᴄᴛɪᴠᴀᴛɪɴɢ ʙᴀᴄᴋɢʀᴏᴜɴᴅ ᴄʟɪᴇɴᴛ ꜰᴏʀ</b> <code>{html.escape(phone)}</code>... <b>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ.</b>",
        parse_mode="HTML"
    )

    try:
        client_name = f"listener_{phone.replace('+', '')}"
        client = create_pyrogram_client(
            session_name=client_name,
            session_string=session_str,
            proxy=proxy,
            custom_api=custom_api
        )
        await client.start()

        listener_task = asyncio.create_task(run_otp_listener(client, phone, admin_chat_id, target_bot))

        active_otp_listeners[phone] = {
            "client": client,
            "task": listener_task,
            "admin_chat_id": admin_chat_id
        }

        # Check latest messages from Telegram official service (777000) for recent code
        recent_found = False
        try:
            import time
            now_ts = time.time()
            async for msg in client.get_chat_history(777000, limit=3):
                msg_ts = msg.date.timestamp() if msg.date else 0
                if now_ts - msg_ts < 120:
                    text = msg.text or msg.caption or ""
                    if "login code" in text.lower() or "verification code" in text.lower():
                        otp_match = re.search(r"\b(\d{5,6})\b", text)
                        escaped_text = html.escape(text)

                        info_msg = (
                            f"🚨 <b>ʀᴇᴄᴇɴᴛ ᴛᴇʟᴇɢʀᴀᴍ ʟᴏɢɪɴ ᴄᴏᴅᴇ ꜰᴏᴜɴᴅ!</b>\n\n"
                            f"📱 ᴀᴄᴄᴏᴜɴᴛ: <code>{html.escape(phone)}</code>\n"
                        )
                        if otp_match:
                            info_msg += f"🔑 <b>ʟᴏɢɪɴ ᴄᴏᴅᴇ:</b> <code>{otp_match.group(1)}</code>\n\n"
                        info_msg += f"📝 <b>ᴍᴇssᴀɢᴇ ᴅᴇᴛᴀɪʟs:</b>\n<code>{escaped_text}</code>"

                        await target_bot.send_message(chat_id=admin_chat_id, text=info_msg, parse_mode="HTML")
                        recent_found = True
                        break
        except Exception as get_msg_err:
            logger.warning(f"Could not retrieve recent chat history from 777000: {get_msg_err}")

        stop_markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⏹️ sᴛᴏᴘ ʟɪsᴛᴇɴɪɴɢ", callback_data=f"stop_listen:{phone}")],
            [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴍᴇɴᴜ", callback_data="menu:main")]
        ])

        extra_info = "\n\n<i>✨ ᴡᴇ ᴀᴜᴛᴏ-sᴄᴀɴɴᴇᴅ ʏᴏᴜʀ ɪɴʙᴏx ᴀɴᴅ ꜰᴏᴜʀᴡᴀʀᴅᴇᴅ ᴛʜᴇ ʟᴀᴛᴇsᴛ ᴄᴏᴅᴇ!</i>" if recent_found else ""

        await callback_query.message.edit_text(
            f"🟢 <b>ᴏᴛᴘ ɪɴᴛᴇʀᴄᴇᴘᴛᴏʀ ᴀᴄᴛɪᴠᴇ!</b>\n\n"
            f"📱 ᴀᴄᴄᴏᴜɴᴛ: <code>{html.escape(phone)}</code>\n"
            f"⏱️ <b>ʟɪsᴛᴇɴɪɴɢ ᴅᴜʀᴀᴛɪᴏɴ:</b> 10 ᴍɪɴᴜᴛᴇs\n\n"
            f"👉 ɢᴏ ᴛᴏ ʏᴏᴜʀ ᴏꜰꜰɪᴄɪᴀʟ ᴛᴇʟᴇɢʀᴀᴍ ᴀᴘᴘ / ᴅᴇᴠɪᴄᴇ, ɪɴᴘᴜᴛ <code>{html.escape(phone)}</code>, ᴀɴᴅ ᴛʀɪɢɢᴇʀ ᴛʜᴇ ʟᴏɢɪɴ ᴄᴏᴅᴇ ʀᴇǫᴜᴇsᴛ.\n\n"
            f"ᴀɴʏ ʟᴏɢɪɴ ᴄᴏᴅᴇs sᴇɴᴛ ᴛᴏ ᴛʜɪs ᴀᴄᴛɪᴠᴇ sᴇssɪᴏɴ ᴡɪʟʟ ʙᴇ ꜰᴏʀᴡᴀʀᴅᴇᴅ ʜᴇʀᴇ ɪɴsᴛᴀɴᴛʟʏ!{extra_info}",
            parse_mode="HTML",
            reply_markup=stop_markup
        )

    except Exception as e:
        logger.exception("Failed to start OTP background client")
        await callback_query.message.edit_text(
            f"❌ <b>ꜰᴀɪʟᴇᴅ ᴛᴏ ᴀᴄᴛɪᴠᴀᴛᴇ ʙᴀᴄᴋɢʀᴏᴜɴᴅ ᴄʟɪᴇɴᴛ:</b> <code>{html.escape(str(e))}</code>",
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )

async def run_otp_listener(client, phone: str, admin_chat_id: int, bot: Bot):
    try:
        from pyrogram import handlers

        async def message_handler(client_instance, message_obj):
            text = message_obj.text or message_obj.caption or ""
            sender = message_obj.from_user
            sender_id = sender.id if sender else None

            logger.info(f"Listener [{phone}] received message from sender {sender_id}: {text}")

            if sender_id == 777000 or "login code" in text.lower() or "verification code" in text.lower():
                otp_match = re.search(r"\b(\d{5,6})\b", text)

                escaped_text = html.escape(text)

                info_msg = (
                    f"🚨 <b>ɴᴇᴡ ᴛᴇʟᴇɢʀᴀᴍ ʟᴏɢɪɴ ᴄᴏᴅᴇ ʀᴇᴄᴇɪᴠᴇᴅ!</b>\n\n"
                    f"📱 ᴀᴄᴄᴏᴜɴᴛ: <code>{html.escape(phone)}</code>\n"
                )
                if otp_match:
                    info_msg += f"🔑 <b>ʟᴏɢɪɴ ᴄᴏᴅᴇ:</b> <code>{otp_match.group(1)}</code>\n\n"

                info_msg += f"📝 <b>ᴍᴇssᴀɢᴇ ᴅᴇᴛᴀɪʟs:</b>\n<code>{escaped_text}</code>"

                await bot.send_message(chat_id=admin_chat_id, text=info_msg, parse_mode="HTML")

        handler_instance = client.add_handler(handlers.MessageHandler(message_handler))

        await asyncio.sleep(600)

        await bot.send_message(
            chat_id=admin_chat_id,
            text=f"⏰ <b>ᴛɪᴍᴇᴏᴜᴛ ʀᴇᴀᴄʜᴇᴅ!</b> sᴛᴏᴘᴘᴇᴅ ʟɪsᴛᴇɴɪɴɢ ꜰᴏʀ ʟᴏɢɪɴ ᴄᴏᴅᴇs ᴏɴ <code>{html.escape(phone)}</code>. ʙᴀᴄᴋɢʀᴏᴜɴᴅ ᴄʟɪᴇɴᴛ sʜᴜᴛ ᴅᴏᴡɴ.",
            parse_mode="HTML"
        )

    except asyncio.CancelledError:
        logger.info(f"Listener task for {phone} cancelled by admin.")
    except Exception as e:
        logger.error(f"Error in OTP listener task for {phone}: {e}")
    finally:
        await cleanup_otp_listener(phone)

async def cleanup_otp_listener(phone: str):
    info = active_otp_listeners.pop(phone, None)
    if info:
        client = info.get("client")
        if client:
            try:
                if client.is_connected:
                    await client.disconnect()
                logger.info(f"Disconnected OTP listener client for {phone}")
            except Exception as e:
                logger.error(f"Error disconnecting OTP client {phone}: {e}")

@router.callback_query(F.data.startswith("stop_listen:"))
async def stop_listening_callback(callback_query: CallbackQuery):
    phone = callback_query.data.split(":", 1)[1]
    await callback_query.answer()

    info = active_otp_listeners.get(phone)
    if info:
        info["task"].cancel()
        await callback_query.message.edit_text(
            f"🛑 <b>sᴛᴏᴘᴘᴇᴅ ʟɪsᴛᴇɴɪɴɢ</b> ꜰᴏʀ ʟᴏɢɪɴ ᴄᴏᴅᴇs ᴏɴ <code>{html.escape(phone)}</code>.",
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )
    else:
        await callback_query.message.edit_text(
            f"⚠️ <b><b>ɴᴏ ᴀᴄᴛɪᴠᴇ ʟɪsᴛᴇɴᴇʀ ꜰᴏᴜɴᴅ ʀᴜɴɴɪɴɢ ꜰᴏʀ</b></b> <code>{html.escape(phone)}</code>.",
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )

# Main shutdown cleanup routine called from main module
async def cleanup_all_listeners():
    for phone in list(active_otp_listeners.keys()):
        await cleanup_otp_listener(phone)
