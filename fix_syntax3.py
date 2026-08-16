with open('plugins/chat_manager.py', 'r') as f:
    lines = f.readlines()

for i in range(len(lines)):
    if "await processing_msg.edit_text(f\"🔍 <b>Search Results for:</b> {html.escape(query)}" in lines[i]:
        lines[i] = lines[i].replace('\n', '\\n').replace('"\n', '"')
        if "Matches:" in lines[i+2]:
             lines[i] += lines[i+1].replace('\n', '\\n') + lines[i+2]
             lines[i+1] = ""
             lines[i+2] = ""

with open('plugins/chat_manager.py', 'w') as f:
    f.writelines([l for l in lines if l != ""])
