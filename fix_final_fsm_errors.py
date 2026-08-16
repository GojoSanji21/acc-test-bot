import re
import glob

# Add Cancel button FSM clear handler to chat_manager.py
with open('plugins/chat_manager.py', 'r') as f:
    chat_content = f.read()

# Make sure imports are present in all plugin files
import_str = "from pyrogram.errors import RPCError, FloodWait, ChatAdminRequired, UserDeactivated, UsernameOccupied, UsernameInvalid, FreshResetAuthorisationForbidden\n"

for file in glob.glob("plugins/*.py"):
    with open(file, 'r') as f:
        content = f.read()

    # Remove old incomplete imports
    content = re.sub(r'from pyrogram\.errors import [^\n]+', '', content)

    # Add new comprehensive import
    if "from pyrogram.errors" not in content:
        # insert after "from pyrogram " or "from aiogram "
        if "from aiogram" in content:
            content = content.replace("from aiogram import", import_str + "from aiogram import")
        else:
            content = import_str + content

    # Fix the missing retry handler in chat_manager.py
    if file.endswith('chat_manager.py'):
        if "process_retry_channel_username" not in content:
            retry_handler = """@router.callback_query(F.data.startswith("retry_chan_username:"))
async def process_retry_channel_username(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    parts = callback_query.data.split(":")
    phone = parts[1]
    page = int(parts[2]) if len(parts) > 2 else 0
    chat_id = parts[3]

    await state.set_state(CreateChannelState.enter_username)
    await state.update_data(phone=phone, page=page, created_chat_id=chat_id)

    await callback_query.message.edit_text(
        "🔗 Send the username (without @) for the public channel:\\n\\nSend /cancel to abort.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ᴄᴀɴᴄᴇʟ", callback_data=f"cancel_wizard:{phone}:{page}")]])
    )
"""
            # Insert before CreateChannelState.enter_username message handler
            content = content.replace("@router.message(CreateChannelState.enter_username)", retry_handler + "\n@router.message(CreateChannelState.enter_username)")

        # Change cancel button to trigger a specific handler
        content = content.replace('callback_data=f"view_acc:{phone}:{page}"', 'callback_data=f"cancel_wizard:{phone}:{page}"')

        # Note: replace some occurrences back to view_acc for the BACK buttons
        content = content.replace('InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"cancel_wizard', 'InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"view_acc')
        content = content.replace('InlineKeyboardButton(text="ʙᴀᴄᴋ ᴛᴏ ᴀᴄᴄᴏᴜɴᴛ", callback_data=f"cancel_wizard', 'InlineKeyboardButton(text="ʙᴀᴄᴋ ᴛᴏ ᴀᴄᴄᴏᴜɴᴛ", callback_data=f"view_acc')

        if "process_cancel_wizard" not in content:
            cancel_handler = """
@router.callback_query(F.data.startswith("cancel_wizard:"))
async def process_cancel_wizard(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer("Wizard Cancelled.")
    await state.clear()

    parts = callback_query.data.split(":")
    phone = parts[1]
    page = parts[2]

    await callback_query.message.edit_text(
        "❌ Action cancelled. Returning to menu.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"view_acc:{phone}:{page}")]])
    )
"""
            content += cancel_handler

    # Fix UserDeactivated in Exception catch
    content = content.replace('except (RPCError, FloodWait, Exception)', 'except (RPCError, FloodWait, ChatAdminRequired, UserDeactivated, Exception)')
    content = content.replace('except (RPCError, FloodWait, ChatAdminRequired, Exception)', 'except (RPCError, FloodWait, ChatAdminRequired, UserDeactivated, Exception)')

    with open(file, 'w') as f:
        f.write(content)
