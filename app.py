import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pytz

# הגדרות
MAX_PLAYERS = 8
DATA_FILE = "players.json"
ISRAEL_TZ = pytz.timezone("Asia/Jerusalem")

# טעינת ושמירת רשימת שחקנים
def load_players():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_players(players):
    with open(DATA_FILE, "w") as f:
        json.dump(players, f)

def is_registration_open():
    now = datetime.now(ISRAEL_TZ)
    day = now.weekday()  # 0=שני ... 4=שישי ... 6=ראשון
    hour = now.hour
    minute = now.minute

    # נפתח ביום שישי מ־14:00
    if day == 4 and (hour >= 14):
        return True
    # פתוח בשבת (שבת = 5)
    if day == 5:
        return True
    # פתוח בראשון (יום ראשון = 6)
    if day == 6:
        return True
    # סגור ביום שני אחרי 1 בלילה
    if day == 0 and hour < 1:
        return True

    return False

# קוד עיקרי
players = load_players()
st.title("הרשמה למשחק פוקר")

# תצוגת רשימת נרשמים תמיד
st.subheader("🎯 שחקנים רשומים כרגע:")
if players:
    for i, p in enumerate(players, start=1):
        st.write(f"{i}. {p}")
else:
    st.info("עדיין אין נרשמים.")

# בדיקה אם ההרשמה פתוחה
if is_registration_open():
    st.markdown("✅ ההרשמה פתוחה כעת!")

    email = st.text_input("הכנס כתובת אימייל שלך")
    action = st.radio("בחר פעולה", ["להירשם למשחק", "להסיר את עצמי"])

    if st.button("שלח"):
        if not email:
            st.warning("יש להזין כתובת אימייל.")
        else:
            if action == "להירשם למשחק":
                if email in players:
                    st.info("כבר נרשמת.")
                elif len(players) >= MAX_PLAYERS:
                    st.error("המשחק מלא! (8 שחקנים)")
                else:
                    players.append(email)
                    save_players(players)
                    st.success("נרשמת בהצלחה!")

            elif action == "להסיר את עצמי":
                if email in players:
                    players.remove(email)
                    save_players(players)
                    st.success("הוסרת מהרשימה.")
                else:
                    st.info("לא נמצאת ברשימת הנרשמים.")

else:
    st.warning("🕐 ההרשמה סגורה. ניתן להירשם מיום שישי ב־14:00 עד יום שני ב־01:00.")

