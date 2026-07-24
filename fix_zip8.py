import re

with open("plugins/add_account.py", "r") as f:
    content = f.read()

search_block = """
                        try:
                            await client.connect()
                            me = await client.get_me()

                            if not me:
                                raise ValueError("Could not retrieve account identity from get_me()")

                            phone = getattr(me, "phone_number", None)
                            if not phone:
                                phone = f"+{me.id}"
                            else:
                                if not phone.startswith("+"):
                                    phone = f"+{phone}"
"""

replace_block = """
                        try:
                            await client.connect()
                            me = await client.get_me()

                            if not me:
                                raise ValueError("Could not retrieve account identity from get_me()")

                            phone = getattr(me, "phone_number", None)
                            if not phone:
                                import re
                                phone_match = re.search(r'\\d+', s_data if s_type == "file" else temp_name)
                                if phone_match:
                                    phone = f"+{phone_match.group(0)}"
                                else:
                                    phone = f"+{me.id}"
                            else:
                                if not phone.startswith("+"):
                                    phone = f"+{phone}"
"""

content = content.replace(search_block.replace("\\n", "\n").strip('\n'), replace_block.replace("\\n", "\n").strip('\n'))

with open("plugins/add_account.py", "w") as f:
    f.write(content)

print("done")
