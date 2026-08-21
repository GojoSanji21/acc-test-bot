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
import random
import emoji
from aiogram import Router, F, Bot, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery, LinkPreviewOptions

from database import get_account, get_all_accounts
from helpers import decrypt_data, create_pyrogram_client

logger = logging.getLogger("TGStorageBot.plugins.login")

router = Router()

IMAGES = [
    'https://graph.org/file/e8af951d867b0aaff8cb0-3205689663c5c662ba.jpg', 'https://graph.org/file/9ce76c7db28dc4daa5f27-b969a50f5a53345633.jpg',
    'https://graph.org/file/3207c5504dc9d45f5d9cf-a8e081cb548479752f.jpg', 'https://graph.org/file/c31949e692d280663d58b-175b7206869b9a2c82.jpg',
    'https://graph.org/file/800c9a3ee9ebc2097d38f-7609d3cf5ae42e41d5.jpg', 'https://graph.org/file/6e6502b5c2d6a68cac1c4-45a1ffc966477471c7.jpg',
    'https://graph.org/file/826a285bb1b76717d6a0e-0a8d4d501cf45fc2db.jpg', 'https://graph.org/file/0a315ee59fbc73bc44326-a766d350855ca79eca.jpg',
    'https://graph.org/file/ac509cacdbc03efbc2e8d-a8ac806b49a71e872d.jpg', 'https://graph.org/file/dd250b63501917843e481-3675d23c4799f97624.jpg',
    'https://graph.org/file/161d918adb1682dd7e301-32d10ea7256daacfa4.jpg', 'https://graph.org/file/7626817e26de338d2e5a1-478b1b721ca9bc63d3.jpg',
    'https://graph.org/file/dd250b63501917843e481-3675d23c4799f97624.jpg', 'https://graph.org/file/9c52583fba67124b6a183-586e58ffeeb840bc5e.jpg',
    'https://graph.org/file/91621631e7dc800ea4562-4b0a9c3601a270556d.jpg', 'https://graph.org/file/91621631e7dc800ea4562-4b0a9c3601a270556d.jpg',
    'https://graph.org/file/4abf7c572c4949e7f657e-3fbcdfd9fc67de5845.jpg', 'https://graph.org/file/89cddd266235b8a806f0e-6504ecc249b2e58ee7.jpg',
    'https://graph.org/file/eace0fc6fa82c0ca3521a-a089e3306f6386977d.jpg', 'https://graph.org/file/a50cde78b6d61ebb76ccd-9d02a956a89fddadd8.jpg',
    'https://graph.org/file/c77152bc70b96db0f079f-0cca0a31c983f97478.jpg', 'https://graph.org/file/019f4539cbecec208972c-c65454256e966a830c.jpg',
    'https://graph.org/file/d7f8b0cf7cf78723b3aee-a5b041281c203e2449.jpg', 'https://graph.org/file/8a012335580d322e7438f-353fbd48e95b00f0f7.jpg',
    'https://graph.org/file/c698be54a12027fb82e69-e9feef426481186208.jpg', 'https://graph.org/file/e3c28bdeb0c2af1b3bbb9-0c5a132aca7f768332.jpg',
    'https://graph.org/file/d8b92bfb4b8932e2ae553-ff9264f5b40c710698.jpg', 'https://graph.org/file/deff1d9b2af3c0740b525-9032f27f051633a627.jpg',
    'https://graph.org/file/a668600b4a516645369fa-465839cfd9e31ecf85.jpg', 'https://graph.org/file/f11e43b3ba09ff1af2eeb-a7d7c86298644597f3.jpg',
    'https://graph.org/file/13b0eaf75f4ffd28cd445-6e5b90592458fc05f1.jpg'
]

def get_preview():
    return LinkPreviewOptions(url=random.choice(IMAGES), prefer_large_media=True, show_above_text=True)

def make_small_caps(text: str) -> str:
    mapping = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ꜰ', 'g': 'ɢ', 'h': 'ʜ',
        'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ', 'p': 'ᴘ',
        'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ', 'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x',
        'y': 'ʏ', 'z': 'ᴢ',
        'A': 'ᴀ', 'B': 'ʙ', 'C': 'ᴄ', 'D': 'ᴅ', 'E': 'ᴇ', 'F': 'ꜰ', 'G': 'ɢ', 'H': 'ʜ',
        'I': 'ɪ', 'J': 'ᴊ', 'K': 'ᴋ', 'L': 'ʟ', 'M': 'ᴍ', 'N': 'ɴ', 'O': 'ᴏ', 'P': 'ᴘ',
        'Q': 'ǫ', 'R': 'ʀ', 'S': 's', 'T': 'ᴛ', 'U': 'ᴜ', 'V': 'ᴠ', 'W': 'ᴡ', 'X': 'x',
        'Y': 'ʏ', 'Z': 'ᴢ'
    }
    # Safely strip emojis and brackets to keep buttons perfectly clean
    text = emoji.replace_emoji(text, replace="")
    text = text.replace("[", "").replace("]", "").strip()
    return "".join(mapping.get(c, c) for c in text)

# Active listeners for OTP retrieval: mapping of phone_number -> listener task / client info
# Each item has: {"client": Client, "task": asyncio.Task, "admin_chat_id": int}
active_otp_listeners = {}

def get_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=make_small_caps("back to main menu"), callback_data="menu:main")]
    ])

@router.callback_query(F.data == "menu:login")
async def start_login_callback(callback_query: CallbackQuery):
    await callback_query.answer()
    accounts = await get_all_accounts(user_id=callback_query.from_user.id)
    if not accounts:
        await callback_query.message.edit_text(
            "📭 <b>ɴᴏ sᴀᴠᴇᴅ ᴛᴇʟᴇɢʀᴀᴍ ᴀᴄᴄᴏᴜɴᴛs ꜰᴏᴜɴᴅ. ᴘʟᴇᴀsᴇ ᴀᴅᴅ ᴀɴ ᴀᴄᴄᴏᴜɴᴛ ꜰɪʀsᴛ.</b>",
            parse_mode="HTML",
            reply_markup=get_back_keyboard(),
            link_preview_options=get_preview()
        )
        return

    keyboard_builder = []
    for acc in accounts:
        phone = acc.get("phone")
        keyboard_builder.append([
            InlineKeyboardButton(text=make_small_caps(f"get otp: {phone}"), callback_data=f"retrieve_otp:{phone}")
        ])
    keyboard_builder.append([InlineKeyboardButton(text=make_small_caps("back to main menu"), callback_data="menu:main")])

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard_builder)
    await callback_query.message.edit_text(
        "🔑 <b>sᴇʟᴇᴄᴛ ᴀɴ ᴀᴄᴄᴏᴜɴᴛ ᴛᴏ ᴛʀɪɢɢᴇʀ ʙᴀᴄᴋɢʀᴏᴜɴᴅ ʟᴏɢɪɴ ᴏᴛᴘ ᴄᴀᴘᴛᴜʀᴇ:</b>",
        reply_markup=markup,
        parse_mode="HTML",
        link_preview_options=get_preview()
    )

@router.message(Command("login"))
async def start_login_handler(message: Message):
    accounts = await get_all_accounts(user_id=message.from_user.id)
    if not accounts:
        await message.answer(
            "📭 <b>ɴᴏ sᴀᴠᴇᴅ ᴛᴇʟᴇɢʀᴀᴍ ᴀᴄᴄᴏᴜɴᴛs ꜰᴏᴜɴᴅ. ᴘʟᴇᴀsᴇ ᴀᴅᴅ ᴀɴ ᴀᴄᴄᴏᴜɴᴛ ꜰɪʀsᴛ.</b>",
            parse_mode="HTML",
            reply_markup=get_back_keyboard(),
            link_preview_options=get_preview()
        )
        return

    keyboard_builder = []
    for acc in accounts:
        phone = acc.get("phone")
        keyboard_builder.append([
            InlineKeyboardButton(text=make_small_caps(f"get otp: {phone}"), callback_data=f"retrieve_otp:{phone}")
        ])
    keyboard_builder.append([InlineKeyboardButton(text=make_small_caps("back to main menu"), callback_data="menu:main")])

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard_builder)
    await message.answer(
        "🔑 <b>sᴇʟᴇᴄᴛ ᴀɴ ᴀᴄᴄᴏᴜɴᴛ ᴛᴏ ᴛʀɪɢɢᴇʀ ʙᴀᴄᴋɢʀᴏᴜɴᴅ ʟᴏɢɪɴ ᴏᴛᴘ ᴄᴀᴘᴛᴜʀᴇ:</b>",
        reply_markup=markup,
        parse_mode="HTML",
        link_preview_options=get_preview()
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
            link_preview_options=get_preview(),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=make_small_caps("stop listening"), callback_data=f"stop_listen:{phone}")],
                [InlineKeyboardButton(text=make_small_caps("back to main menu"), callback_data="menu:main")]
            ])
        )
        return

    acc = await get_account(phone, user_id=callback_query.from_user.id)
    if not acc:
        await callback_query.message.edit_text(
            "❌ <b>sᴇʟᴇᴄᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛ ɴᴏ ʟᴏɴɢᴇʀ ᴇxɪsᴛs ɪɴ ᴅᴀᴛᴀʙᴀsᴇ.</b>",
            reply_markup=get_back_keyboard(),
            parse_mode="HTML",
            link_preview_options=get_preview()
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
            parse_mode="HTML",
            link_preview_options=get_preview()
        )
        return

    await callback_query.message.edit_text(
        f"⏳ <b>ᴀᴄᴛɪᴠᴀᴛɪɴɢ ʙᴀᴄᴋɢʀᴏᴜɴᴅ ᴄʟɪᴇɴᴛ ꜰᴏʀ</b> <code>{html.escape(phone)}</code>... <b>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ.</b>",
        parse_mode="HTML",
        link_preview_options=get_preview()
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

                        await target_bot.send_message(
                            chat_id=admin_chat_id, 
                            text=info_msg, 
                            parse_mode="HTML",
                            link_preview_options=get_preview()
                        )
                        recent_found = True
                        break
        except Exception as get_msg_err:
            logger.warning(f"Could not retrieve recent chat history from 777000: {get_msg_err}")

        stop_markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=make_small_caps("stop listening"), callback_data=f"stop_listen:{phone}")],
            [InlineKeyboardButton(text=make_small_caps("back to main menu"), callback_data="menu:main")]
        ])

        extra_info = "\n\n<i>✨ ᴡᴇ ᴀᴜᴛᴏ-sᴄᴀɴɴᴇᴅ ʏᴏᴜʀ ɪɴʙᴏx ᴀɴᴅ ꜰᴏᴜʀᴡᴀʀᴅᴇᴅ ᴛʜᴇ ʟᴀᴛᴇsᴛ ᴄᴏᴅᴇ!</i>" if recent_found else ""

        await callback_query.message.edit_text(
            f"🟢 <b>ᴏᴛᴘ ɪɴᴛᴇʀᴄᴇᴘᴛᴏʀ ᴀᴄᴛɪᴠᴇ!</b>\n\n"
            f"📱 ᴀᴄᴄᴏᴜɴᴛ: <code>{html.escape(phone)}</code>\n"
            f"⏱️ <b>ʟɪsᴛᴇɴɪɴɢ ᴅᴜʀᴀᴛɪᴏɴ:</b> 10 ᴍɪɴᴜᴛᴇs\n\n"
            f"👉 ɢᴏ ᴛᴏ ʏᴏᴜʀ ᴏꜰꜰɪᴄɪᴀʟ ᴛᴇʟᴇɢʀᴀᴍ ᴀᴘᴘ / ᴅᴇᴠɪᴄᴇ, ɪɴᴘᴜᴛ <code>{html.escape(phone)}</code>, ᴀɴᴅ ᴛʀɪɢɢᴇʀ ᴛʜᴇ ʟᴏɢɪɴ ᴄᴏᴅᴇ ʀᴇǫᴜᴇsᴛ.\n\n"
            f"ᴀɴʏ ʟᴏɢɪɴ ᴄᴏᴅᴇs sᴇɴᴛ ᴛᴏ ᴛʜɪs ᴀᴄᴛɪᴠᴇ sᴇssɪᴏɴ ᴡɪʟʟ ʙᴇ ꜰᴏʀᴡᴀʀᴅᴇᴅ ʜᴇʀᴇ ɪɴsᴛᴀɴᴛʟʏ!{extra_info}",
            parse_mode="HTML",
            reply_markup=stop_markup,
            link_preview_options=get_preview()
        )

    except Exception as e:
        logger.exception("Failed to start OTP background client")
        await callback_query.message.edit_text(
            f"❌ <b>ꜰᴀɪʟᴇᴅ ᴛᴏ ᴀᴄᴛɪᴠᴀᴛᴇ ʙᴀᴄᴋɢʀᴏᴜɴᴅ ᴄʟɪᴇɴᴛ:</b> <code>{html.escape(str(e))}</code>",
            parse_mode="HTML",
            reply_markup=get_back_keyboard(),
            link_preview_options=get_preview()
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

                await bot.send_message(
                    chat_id=admin_chat_id, 
                    text=info_msg, 
                    parse_mode="HTML",
                    link_preview_options=get_preview()
                )

        handler_instance = client.add_handler(handlers.MessageHandler(message_handler))

        await asyncio.sleep(600)

        await bot.send_message(
            chat_id=admin_chat_id,
            text=f"⏰ <b>ᴛɪᴍᴇᴏᴜᴛ ʀᴇᴀᴄʜᴇᴅ!</b> sᴛᴏᴘᴘᴇᴅ ʟɪsᴛᴇɴɪɴɢ ꜰᴏʀ ʟᴏɢɪɴ ᴄᴏᴅᴇs ᴏɴ <code>{html.escape(phone)}</code>. ʙᴀᴄᴋɢʀᴏᴜɴᴅ ᴄʟɪᴇɴᴛ sʜᴜᴛ ᴅᴏᴡɴ.",
            parse_mode="HTML",
            link_preview_options=get_preview()
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
                    await client.stop()
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
            reply_markup=get_back_keyboard(),
            link_preview_options=get_preview()
        )
    else:
        await callback_query.message.edit_text(
            f"⚠️ <b><b>ɴᴏ ᴀᴄᴛɪᴠᴇ ʟɪsᴛᴇɴᴇʀ ꜰᴏᴜɴᴅ ʀᴜɴɴɪɴɢ ꜰᴏʀ</b></b> <code>{html.escape(phone)}</code>.",
            parse_mode="HTML",
            reply_markup=get_back_keyboard(),
            link_preview_options=get_preview()
        )

# Main shutdown cleanup routine called from main module
async def cleanup_all_listeners():
    for phone in list(active_otp_listeners.keys()):
        await cleanup_otp_listener(phone)
