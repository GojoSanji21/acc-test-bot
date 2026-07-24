with open("plugins/add_account.py", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line == '                            f"✅ <b>ᴀᴄᴄᴏᴜɴᴛ ᴀᴅᴅᴇᴅ sᴜᴄssꜰᴜʟʟʏ ᴠɪᴀ ᴜᴘʟᴏᴀᴅ!</b>\n' or line == '                            f"✅ <b>ᴀᴄᴄᴏᴜɴᴛ ᴀᴅᴅᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴠɪᴀ ᴜᴘʟᴏᴀᴅ!</b>\n':
        new_lines.append('                            f"✅ <b>ᴀᴄᴄᴏᴜɴᴛ ᴀᴅᴅᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴠɪᴀ ᴜᴘʟᴏᴀᴅ!</b>\\n\\n"\n')
    elif line == '                            f"👤 <b>ɴᴀᴍᴇ:</b> <code>{html.escape(profile_name)}</code>\n':
        new_lines.append('                            f"👤 <b>ɴᴀᴍᴇ:</b> <code>{html.escape(profile_name)}</code>\\n"\n')
    elif line == '                            f"📱 <b>ᴘʜᴏɴᴇ:</b> <code>{html.escape(phone)}</code>\n':
        new_lines.append('                            f"📱 <b>ᴘʜᴏɴᴇ:</b> <code>{html.escape(phone)}</code>\\n"\n')
    elif line == '                            f"🔒 <b>sᴇssɪᴏɴ sᴛʀɪɴɢ:</b> ᴇɴᴄʀʏᴘᴛᴇᴅ &amp; sᴀᴠᴇᴅ sᴇᴄᴜʀᴇʟʏ.\n':
        new_lines.append('                            f"🔒 <b>sᴇssɪᴏɴ sᴛʀɪɴɢ:</b> ᴇɴᴄʀʏᴘᴛᴇᴅ &amp; sᴀᴠᴇᴅ sᴇᴄᴜʀᴇʟʏ.\\n"\n')
    elif line == '                            f"🌐 <b>ʙᴏᴜɴᴅ ᴘʀᴏxʏ:</b> {proxy_info}\n':
        new_lines.append('                            f"🌐 <b>ʙᴏᴜɴᴅ ᴘʀᴏxʏ:</b> {proxy_info}\\n\\n"\n')
    elif line == '\n' or line == '"\n':
        pass
    else:
        new_lines.append(line)

with open("plugins/add_account.py", "w") as f:
    f.write("".join(new_lines))

print("done")
