with open("app.py", "r", encoding='utf-8') as f:
    lines = f.readlines()
lines = lines[:3407] + lines[3639:]
with open("app.py", "w", encoding='utf-8') as f:
    f.writelines(lines)