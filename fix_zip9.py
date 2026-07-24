with open("plugins/add_account.py", "r") as f:
    content = f.read()

search_block = """
                            f"✅ <b>ᴀᴄᴄᴏᴜɴᴛ ᴀᴅᴅᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴠɪᴀ ᴜᴘʟᴏᴀᴅ!</b>

"
                            f"👤 <b>ɴᴀᴍᴇ:</b> <code>{html.escape(profile_name)}</code>
"
                            f"📱 <b>ᴘʜᴏɴᴇ:</b> <code>{html.escape(phone)}</code>
"
                            f"🔒 <b>sᴇssɪᴏɴ sᴛʀɪɴɢ:</b> ᴇɴᴄʀʏᴘᴛᴇᴅ &amp; sᴀᴠᴇᴅ sᴇᴄᴜʀᴇʟʏ.
"
                            f"🌐 <b>ʙᴏᴜɴᴅ ᴘʀᴏxʏ:</b> {proxy_info}

"
                            f"ʏᴏᴜ ᴄᴀɴ ɴᴏᴡ ᴍᴀɴᴀɢᴇ ᴛʜɪs sᴇssɪᴏɴ inside the account panel.",
"""

replace_block = """
                            f"✅ <b>ᴀᴄᴄᴏᴜɴᴛ ᴀᴅᴅᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴠɪᴀ ᴜᴘʟᴏᴀᴅ!</b>\\n\\n"
                            f"👤 <b>ɴᴀᴍᴇ:</b> <code>{html.escape(profile_name)}</code>\\n"
                            f"📱 <b>ᴘʜᴏɴᴇ:</b> <code>{html.escape(phone)}</code>\\n"
                            f"🔒 <b>sᴇssɪᴏɴ sᴛʀɪɴɢ:</b> ᴇɴᴄʀʏᴘᴛᴇᴅ &amp; sᴀᴠᴇᴅ sᴇᴄᴜʀᴇʟʏ.\\n"
                            f"🌐 <b>ʙᴏᴜɴᴅ ᴘʀᴏxʏ:</b> {proxy_info}\\n\\n"
                            f"ʏᴏᴜ ᴄᴀɴ ɴᴏᴡ ᴍᴀɴᴀɢᴇ ᴛʜɪs sᴇssɪᴏɴ inside the account panel.",
"""

content = content.replace(search_block.strip('\n'), replace_block.replace("\\n", "\n").strip('\n'))

with open("plugins/add_account.py", "w") as f:
    f.write(content)

print("done")
