import streamlit as st
import json
import os
from datetime import datetime
import pytz

# ===== הגדרות =====
MAX_PLAYERS = 8
DATA_FILE = "players.json"
ALL_PLAYERS_FILE = "all_players.json"
LAST_RESET_FILE = "last_reset.txt"
ISRAEL_TZ = pytz.timezone("Asia/Jerusalem")
ADMIN_CODE = "secretadmin"  # שנה לקוד שלך

# ===== פונקציות עזר =====
def load_json(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r") as f:
        return json.load(f)

def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f)

def get_player(name, players):
    for p in players:
        if p["name"] == name:
            return p
    return None

def is_registration_open(now):
    day = now.weekday()
    hour = now.hour
    if day == 4 and hour >= 18:
        return True
    if day in [5, 6]:
        return True
    if day == 0 and hour < 1:
        return True
    return False

def is_new_registration_period(now):
    if not os.path.exists(LAST_RESET_FILE):
        with open(LAST_RESET_FILE, "w") as f:
            f.write(now.strftime("%Y-%m-%d"))
        return True

    with open(LAST_RESET_FILE, "r") as f:
        last_reset = datetime.strptime(f.read(), "%Y-%m-%d").date()

    if now.weekday() == 4 and now.hour >= 18:
        if now.date() != last_reset:
            with open(LAST_RESET_FILE, "w") as f:
                f.write(now.strftime("%Y-%m-%d"))
            return True
    return False

def reset_registration():
    save_json(DATA_FILE, [])

def auto_register_missing_players(all_players, registered_players):
    current_names = [p["name"] for p in registered_players]
    missing = [p for p in all_players if p["name"] not in current_names]

    for p in missing:
        if len(registered_players) >= MAX_PLAYERS:
            break
        registered_players.append(p)

    save_json(DATA_FILE, registered_players)

# ===== התחלה =====
now = datetime.now(ISRAEL_TZ)
all_players = load_json(ALL_PLAYERS_FILE)
players = load_json(DATA_FILE)

if is_new_registration_period(now):
    reset_registration()
    players = []
    auto_register_missing_players(all_players, players)

# ===== ממשק ראשי =====
st.title("הרשמה למשחק פוקר")

st.subheader("🌟 שחקנים רשומים כרגע:")
if players:
    for i, p in enumerate(players, start=1):
        st.write(f"{i}. {p['name']}")
else:
    st.info("אין נרשמים עדיין.")

st.markdown("---")
st.header("📊 טופס פעולה")

name = st.text_input("שם משתמש")
code = st.text_input("קוד אישי או קוד אדמין", type="password")
action = st.radio("בחר פעולה", ["להירשם למשחק", "להסיר את עצמי", "🛠️ אדמין - איפוס קוד"])
new_code = None

if action == "🛠️ אדמין - איפוס קוד" and code == ADMIN_CODE:
    new_code = st.text_input("🔐 קוד חדש לשחקן", type="password")

if st.button("שלח"):
    if not name.strip() or not code.strip():
        st.warning("יש להזין שם וקוד.")
    else:
        allowed_player = get_player(name, all_players)
        existing_player = get_player(name, players)

        if action == "להירשם למשחק":
            if not is_registration_open(now):
                st.error("ההרשמה סגורה.")
            elif not allowed_player:
                st.error("שחקן לא קיים ברשימה הקבועה.")
            elif allowed_player["code"] != code:
                st.error("קוד אישי שגוי.")
            elif existing_player:
                st.info("כבר נרשמת.")
            elif len(players) >= MAX_PLAYERS:
                st.error("המשחק מלא.")
            else:
                players.append(allowed_player)
                save_json(DATA_FILE, players)
                st.success(f"{name} נרשמת בהצלחה!")

        elif action == "להסיר את עצמי":
            if existing_player and existing_player["code"] == code:
                players = [p for p in players if p["name"] != name]
                save_json(DATA_FILE, players)
                st.success("הוסרת מהרשימה.")
            else:
                st.error("שם או קוד שגויים.")

        elif action == "🛠️ אדמין - איפוס קוד":
            if code != ADMIN_CODE:
                st.error("קוד אדמין שגוי.")
            elif not new_code:
                st.warning("הכנס קוד חדש.")
            else:
                target = get_player(name, all_players)
                if not target:
                    st.error("המשתמש לא נמצא ברשימה.")
                else:
                    target["code"] = new_code
                    save_json(ALL_PLAYERS_FILE, all_players)
                    for p in players:
                        if p["name"] == name:
                            p["code"] = new_code
                    save_json(DATA_FILE, players)
                    st.success(f"הקוד של '{name}' עודכן בהצלחה ✅")
