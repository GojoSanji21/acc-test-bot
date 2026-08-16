import re

with open('plugins/chat_manager.py', 'r') as f:
    chat_content = f.read()

# 2. Add Send Message & Delete/Leave to Chat Control Panel
panel_search = """        keyboard = [
            [
                InlineKeyboardButton(text="ᴄʜᴀɴɢᴇ ɴᴀᴍᴇ", callback_data=f"chat_act:rename:{chat.id}:{phone}:{page}"),
                InlineKeyboardButton(text="ᴄʜᴀɴɢᴇ ᴘʜᴏᴛᴏ", callback_data=f"chat_act:photo:{chat.id}:{phone}:{page}")
            ],
            [
                InlineKeyboardButton(text="ᴍᴀᴋᴇ ᴘᴜʙʟɪᴄ" if not chat.username else "ᴍᴀᴋᴇ ᴘʀɪᴠᴀᴛᴇ", callback_data=f"chat_act:privacy:{chat.id}:{phone}:{page}"),
                InlineKeyboardButton(text="ᴘʀᴏᴍᴏᴛᴇ ᴀᴅᴍɪɴ", callback_data=f"chat_act:admin:{chat.id}:{phone}:{page}")
            ],
            [InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"view_acc:{phone}:{page}")]
        ]"""

panel_replace = """        keyboard = [
            [
                InlineKeyboardButton(text="ᴄʜᴀɴɢᴇ ɴᴀᴍᴇ", callback_data=f"chat_act:rename:{chat.id}:{phone}:{page}"),
                InlineKeyboardButton(text="ᴄʜᴀɴɢᴇ ᴜsᴇʀɴᴀᴍᴇ", callback_data=f"chat_act:privacy:{chat.id}:{phone}:{page}")
            ],
            [
                InlineKeyboardButton(text="sᴇɴᴅ ᴍᴇssᴀɢᴇ", callback_data=f"chat_act:send_msg:{chat.id}:{phone}:{page}"),
                InlineKeyboardButton(text="ᴘʀᴏᴍᴏᴛᴇ ᴀᴅᴍɪɴ", callback_data=f"chat_act:admin:{chat.id}:{phone}:{page}")
            ],
            [
                InlineKeyboardButton(text="ᴘᴜʙʟɪᴄ ʟɪɴᴋ" if chat.username else "ᴘʀɪᴠᴀᴛᴇ ʟɪɴᴋ", url=f"https://t.me/{chat.username}" if chat.username else (chat.invite_link or f"https://t.me/c/{str(chat.id).replace('-100', '')}/1")),
                InlineKeyboardButton(text="ᴅᴇʟᴇᴛᴇ ᴄʜᴀɴɴᴇʟ" if chat.type.name == "CHANNEL" else "ʟᴇᴀᴠᴇ ᴄʜᴀᴛ", callback_data=f"chat_act:delete:{chat.id}:{phone}:{page}")
            ],
            [InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"view_acc:{phone}:{page}")]
        ]"""

chat_content = chat_content.replace(panel_search, panel_replace)
print("Replaced panel")

with open('plugins/chat_manager.py', 'w') as f:
    f.write(chat_content)
