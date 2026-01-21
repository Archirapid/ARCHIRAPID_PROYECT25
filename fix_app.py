with open('c:/ARCHIRAPID_PROYECT25/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Cambiar la línea 2346 (0-indexed 2345)
lines[2345] = '                if not st.session_state.get("logged_in", False) or not st.session_state.get("email", ""):\n'

with open('c:/ARCHIRAPID_PROYECT25/app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Fixed line 2347')