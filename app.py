import streamlit as st
import json
import os
from datetime import datetime
import pytz

# הגדרות
MAX_PLAYERS = 8
DATA_FILE = "players.json"
ALL_PLAYERS_FILE = "all_players.json"
ISRAEL_TZ = pytz.timezone("Asia/Jerusalem")
ADMIN_CODE = "secretadmin"  # שנה לקוד שלך

# טעינת/שמירת JSON
def load_json(file):
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

# פונקציות זמן והרשמה
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
    last_reset_file = "last_reset.txt"
    if not os.path.exists(last_reset_file):
        with open(last_reset_file, "w") as f:
            f.write(now.strftime("%Y-%m-%d"))
        return True

    with open(last_reset_file, "r") as f:
        last_reset = datetime.strptime(f.read(), "%Y-%m-%d").date()

    if now.weekday() == 4 and now.hour >= 18:
        if now.date() != last_reset:
            with open(last_reset_file, "w") as f:
                f.write(now.strftime("%Y-%m-%d"))
            return True
    return False

def reset_registration():
    save_json(DATA_FILE, [])

def auto_register_from_all(all_players, registered_players):
    current_names = [p["name"] for p in registered_players]
    missing_players = [p for p in all_players if p["name"] not in current_names]

    for p in missing_players:
        if len(registered_players) >= MAX_PLAYERS:
            break
        registered_players.append(p)

    save_json(DATA_FILE, registered_players)

def get_player(name, players):
    for p in players:
        if p["name"] == name:
            return p
    return None

# התחלה
now = datetime.now(ISRAEL_TZ)

if is_new_registration_period(now):
    reset_registration()
    all_players = load_json(ALL_PLAYERS_FILE)
    players = []
    auto_register_from_all(all_players, players)

players = load_json(DATA_FILE)
all_players = load_json(ALL_PLAYERS_FILE)

st.title("הרשמה למשחק פוקר")

# הצגת שחקנים רשומים
st.subheader("🎯 שחקנים רשומים כרגע:")
if players:
    for i, p in enumerate(players, start=1):
        st.write(f"{i}. {p['name']}")
else:
    st.info("אין נרשמים עדיין.")

# טופס פעולה
st.markdown("---")
st.header("📥 טופס פעולה")

name = st.text_input("שם משתמש")
code = st.text_input("קוד אישי (או קוד אדמין)", type="password")
action = st.radio("בחר פעולה", ["להירשם למשחק", "להסיר את עצמי", "🛠️ אדמין - איפוס קוד"])

if st.button("שלח"):
    if not name.strip() or not code.strip():
        st.warning("יש להזין שם וקוד.")
    else:
        player = get_player(name, players)
        allowed_player = get_player(name, all_players)

        if action == "להירשם למשחק":
            if not allowed_player:
                st.error("⚠️ שחקן לא קיים ברשימה הקבועה. פנה לאדמין.")
            elif allowed_player["code"] != code:
                st.error("❌ קוד אישי שגוי.")
            elif player:
                st.info("כבר נרשמת.")
            elif len(players) >= MAX_PLAYERS:
                st.error("המשחק מלא (8 שחקנים).")
            else:
                players.append(allowed_player)
                save_json(DATA_FILE, players)
                st.success(f"{name} נרשמת בהצלחה!")

        elif action == "להסיר את עצמי":
            if player and player["code"] == code:
                players = [p for p in players if p["name"] != name]
                save_json(DATA_FILE, players)
                st.success("הוסרת מהרשימה.")
            else:
                st.error("שם או קוד שגויים.")

        elif action == "🛠️ אדמין - איפוס קוד":
            if code != ADMIN_CODE:
                st.error("קוד אדמין שגוי.")
            else:
                new_code = st.text_input("קוד חדש לשחקן", type="password")
                if st.button("אפס סיסמה"):
                    target = get_player(name, all_players)
                    if not target:
                        st.error("המשתמש לא נמצא.")
                    else:
                        target["code"] = new_code
                        save_json(ALL_PLAYERS_FILE, all_players)
                        for p in players:
                            if p["name"] == name:
                                p["code"] = new_code
                        save_json(DATA_FILE, players)
                        st.success(f"הקוד של '{name}' אופס בהצלחה.")
