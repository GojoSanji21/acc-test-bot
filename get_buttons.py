import os
import re

for file in os.listdir('plugins'):
    if file.endswith('.py'):
        path = os.path.join('plugins', file)
        with open(path, 'r') as f:
            content = f.read()
            matches = re.findall(r'text=(f?"[^"]+")', content)
            print(f"--- {file} ---")
            for m in set(matches):
                print(m)
