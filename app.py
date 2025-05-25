import streamlit as st
import json
import os
from datetime import datetime
import pytz

MAX_PLAYERS = 8
DATA_FILE = "players.json"
ISRAEL_TZ = pytz.timezone("Asia/Jerusalem")
ADMIN_CODE = "secretadmin"  # שנה לקוד משלך

# פונקציות עזר
def load_players():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_players(players):
    with open(DATA_FILE, "w") as f:
        json.dump(players, f)

def clear_players():
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)

def is_registration_open(now):
    day = now.weekday()
    hour = now.hour
    if day == 4 and hour >= 14:
        return True
    if day in [5, 6]:
        return True
    if day == 0 and hour < 1:
        return True
    return False

def should_clear_list(now):
    return now.weekday() == 1 and now.hour >= 20

def get_player(name, players):
    for p in players:
        if p["name"] == name:
            return p
    return None

now = datetime.now(ISRAEL_TZ)
players = load_players()

# איפוס שלישי בלילה
if should_clear_list(now):
    clear_players()
    players = []

st.title("הרשמה למשחק פוקר")

# הצגת נרשמים תמיד
st.subheader("🎯 שחקנים רשומים כרגע:")
if players:
    for i, p in enumerate(players, start=1):
        st.write(f"{i}. {p['name']}")
else:
    st.info("אין נרשמים עדיין.")

# טופס למשתמשים
st.markdown("---")
st.header("📥 טופס פעולה")

name = st.text_input("שם משתמש")
code = st.text_input("קוד אישי (או קוד אדמין)", type="password")
action = st.radio("בחר פעולה", ["להירשם למשחק", "להסיר את עצמי", "🛠️ אדמין - איפוס קוד"])

if st.button("שלח"):
    if not name.strip() or not code.strip():
        st.warning("יש להזין גם שם וגם קוד.")
    else:
        player = get_player(name, players)

        # הרשמה רגילה
        if action == "להירשם למשחק":
            if player:
                if player["code"] == code:
                    st.info("כבר נרשמת.")
                else:
                    st.error("שם כבר קיים עם קוד אחר.")
            elif len(players) >= MAX_PLAYERS:
                st.error("המשחק מלא.")
            else:
                players.append({"name": name, "code": code})
                save_players(players)
                st.success("נרשמת בהצלחה!")

        # הסרה
        elif action == "להסיר את עצמי":
            if player and player["code"] == code:
                players = [p for p in players if p["name"] != name]
                save_players(players)
                st.success("הוסרת מהרשימה.")
            else:
                st.error("שם או קוד שגויים. לא ניתן להסיר.")

        # אדמין: איפוס קוד
        elif action == "🛠️ אדמין - איפוס קוד":
            if code != ADMIN_CODE:
                st.error("קוד אדמין שגוי.")
            else:
                new_code = st.text_input("הזן קוד חדש לשחקן", type="password")
                if st.button("אפס סיסמה"):
                    if not player:
                        st.error("שם לא קיים.")
                    else:
                        player["code"] = new_code
                        save_players(players)
                        st.success(f"הקוד של '{name}' אופס בהצלחה.")
