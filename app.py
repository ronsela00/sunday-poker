import streamlit as st
import json
import os
from datetime import datetime
import pytz

# הגדרות
MAX_PLAYERS = 8
DATA_FILE = "players.json"
ISRAEL_TZ = pytz.timezone("Asia/Jerusalem")

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
    day = now.weekday()  # 0=שני, 4=שישי, 6=ראשון
    hour = now.hour

    if day == 4 and hour >= 14:  # שישי מ-14:00
        return True
    if day in [5, 6]:  # שבת וראשון
        return True
    if day == 0 and hour < 1:  # שני עד 01:00
        return True
    return False

def should_clear_list(now):
    return now.weekday() == 1 and now.hour >= 20  # שלישי מ-20:00

# קוד ראשי
now = datetime.now(ISRAEL_TZ)
players = load_players()

# איפוס רשימה בשלישי בערב
if should_clear_list(now):
    clear_players()
    players = []

st.title("הרשמה למשחק פוקר")

# תצוגת הרשימה תמיד עד שלישי בערב
st.subheader("🎯 שחקנים רשומים כרגע:")
if players:
    for i, p in enumerate(players, start=1):
        st.write(f"{i}. {p}")
else:
    st.info("אין כרגע נרשמים.")

# הצגת טופס רק בזמני הרשמה
if is_registration_open(now):
    st.markdown("✅ ההרשמה פתוחה כעת!")

    username = st.text_input("שם משתמש")
    action = st.radio("בחר פעולה", ["להירשם למשחק", "להסיר את עצמי"])

    if st.button("שלח"):
        if not username.strip():
            st.warning("יש להזין שם שחקן.")
        else:
            if action == "להירשם למשחק":
                if username in players:
                    st.info("כבר נרשמת.")
                elif len(players) >= MAX_PLAYERS:
                    st.error("המשחק מלא! (8 שחקנים)")
                else:
                    players.append(username)
                    save_players(players)
                    st.success("נרשמת בהצלחה!")

            elif action == "להסיר את עצמי":
                if username in players:
                    players.remove(username)
                    save_players(players)
                    st.success("הוסרת מהרשימה.")
                else:
                    st.info("לא נמצאת ברשימת הנרשמים.")
else:
    st.warning("🕐 ההרשמה סגורה. ניתן להירשם מיום שישי ב־14:00 עד יום שני ב־01:00.")
