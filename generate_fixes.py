import re

with open('plugins/chat_manager.py', 'r') as f:
    chat_content = f.read()

# 1. Fix get_authorizations
auth_search = """        authorizations = await client.get_authorizations()

        text = "📱 <b>ᴀᴄᴛɪᴠᴇ ᴅᴇᴠɪᴄᴇs</b>\\n━━━━━━━━━━━━━━━━━━━━━\\n"
        keyboard = []

        for auth in authorizations:
            if auth.is_current:"""

auth_replace = """        from pyrogram.raw import functions as raw_functions
        from pyrogram.raw import types as raw_types
        authorizations = await client.invoke(raw_functions.account.GetAuthorizations())

        text = "📱 <b>ᴀᴄᴛɪᴠᴇ ᴅᴇᴠɪᴄᴇs</b>\\n━━━━━━━━━━━━━━━━━━━━━\\n"
        keyboard = []

        for auth in authorizations.authorizations:
            if getattr(auth, 'current', False):"""

chat_content = chat_content.replace(auth_search, auth_replace)

auth_search2 = """            else:
                info = f"{auth.app_name} - {auth.device_model} ({auth.platform})"
                keyboard.append([InlineKeyboardButton(text=f"❌ Terminate: {info[:20]}...", callback_data=f"term_dev:{phone}:{auth.hash}")])"""

auth_replace2 = """            else:
                info = f"{getattr(auth, 'app_name', 'Unknown')} - {getattr(auth, 'device_model', 'Unknown')} ({getattr(auth, 'platform', 'Unknown')})"
                keyboard.append([InlineKeyboardButton(text=f"❌ Terminate: {info[:20]}...", callback_data=f"term_dev:{phone}:{auth.hash}")])"""

chat_content = chat_content.replace(auth_search2, auth_replace2)

print("Replaced 1")

auth_search3 = """        authorizations = await client.get_authorizations()
        count = 0
        for auth in authorizations:
            if not auth.is_current:
                await client.reset_authorization(auth.hash)
                count += 1"""

auth_replace3 = """        from pyrogram.raw import functions as raw_functions
        from pyrogram.raw import types as raw_types
        authorizations = await client.invoke(raw_functions.account.GetAuthorizations())
        count = 0
        for auth in authorizations.authorizations:
            if not getattr(auth, 'current', False):
                try:
                    await client.invoke(raw_functions.account.ResetAuthorization(hash=auth.hash))
                    count += 1
                except Exception as e:
                    logger.error(f"Failed to reset auth: {e}")"""

chat_content = chat_content.replace(auth_search3, auth_replace3)
print("Replaced 3")

term_dev_search = """        await client.reset_authorization(int(auth_hash))
        await callback_query.answer("✅ Device terminated successfully.", show_alert=True)
        # Refresh list
        await process_active_devices(callback_query)"""

term_dev_replace = """        from pyrogram.raw import functions as raw_functions
        await client.invoke(raw_functions.account.ResetAuthorization(hash=int(auth_hash)))
        await callback_query.answer("✅ Device terminated successfully.", show_alert=True)
        # Refresh list
        await process_active_devices(callback_query)"""

chat_content = chat_content.replace(term_dev_search, term_dev_replace)
print("Replaced 4")

with open('plugins/chat_manager.py', 'w') as f:
    f.write(chat_content)
