import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pytz

# הגדרות
MAX_PLAYERS = 8
DATA_FILE = "players.json"
ALL_PLAYERS_FILE = "all_players.json"
ISRAEL_TZ = pytz.timezone("Asia/Jerusalem")
ADMIN_CODE = "secretadmin"  # שנה לקוד שלך

# פונקציות לקבצים
def load_json(file):
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

# בדיקה אם ההרשמה פתוחה
def is_registration_open(now):
    day = now.weekday()
    hour = now.hour
    if day == 4 and hour >= 18:  # שישי מ-18:00
        return True
    if day in [5, 6]:  # שבת, ראשון
        return True
    if day == 0 and hour < 1:  # שני עד 01:00
        return True
    return False

# בדיקה אם זו הרשמה חדשה (כל שבוע)
def is_new_registration_period(now):
    last_reset_file = "last_reset.txt"
    if not os.path.exists(last_reset_file):
        with open(last_reset_file, "w") as f:
            f.write(now.strftime("%Y-%m-%d"))
        return True

    with open(last_reset_file, "r") as f:
        last_reset = datetime.strptime(f.read(), "%Y-%m-%d").date()

    # אם עכשיו שישי 18:00 או יותר, והשבוע שונה מהשבוע האחרון ששמרנו
    if now.weekday() == 4 and now.hour >= 18:
        if now.date() != last_reset:
            with open(last_reset_file, "w") as f:
                f.write(now.strftime("%Y-%m-%d"))
            return True
    return False

# ניקוי רשימת נרשמים ישנה והוספת שחקנים שלא נרשמו מהרשימה הקבועה
def reset_registration():
    players = []
    save_json(DATA_FILE, players)

def auto_register_from_all(all_players, registered_players):
    current_names = [p["name"] for p in registered_players]
    missing_players = [p for p in all_players if p["name"] not in current_names]

    for p in missing_players:
        registered_players.append(p)
    save_json(DATA_FILE, registered_players)

# פונקציות עזר נוספות
def get_player(name, players):
    for p in players:
        if p["name"] == name:
            return p
    return None

# התחלה
now = datetime.now(ISRAEL_TZ)

# אם התחיל מחזור הרשמה חדש – אפס והרשם אוטומטית את החסרים
if is_new_registration_period(now):
    reset_registration()
    all_players = load_json(ALL_PLAYERS_FILE)
    auto_register_from_all(all_players, [])

# טוען שחקנים
players = load_json(DATA_FILE)
all_players = load_json(ALL_PLAYERS_FILE)

st.title("הרשמה למשחק פוקר")

# הצגת רשימה תמיד
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
        st.warning("יש להזין גם שם וגם קוד.")
    else:
        player = get_player(name, players)

        if action == "להירשם למשחק":
            allowed_player = get_player(name, all_players)
            if not allowed_player:
                st.error("⚠️ שחקן לא קיים ברשימה הקבועה. נא לפנות לאדמין.")
            elif allowed_player["code"] != code:
                st.error("❌ קוד אישי שגוי.")
            elif get_player(name, players):
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
                        # עדכון גם אם הוא רשום כרגע
                        for p in players:
                            if p["name"] == name:
                                p["code"] = new_code
                        save_json(DATA_FILE, players)
                        st.success(f"הקוד של '{name}' אופס בהצלחה.")
