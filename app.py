import streamlit as st
import json
import os
from datetime import datetime
import pytz

# ===== הגדרות =====
MAX_PLAYERS = 8
MIN_PLAYERS = 6
DATA_FILE = "players.json"
LAST_RESET_FILE = "last_reset.txt"
ISRAEL_TZ = pytz.timezone("Asia/Jerusalem")

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

# ===== התחלה =====
now = datetime.now(ISRAEL_TZ)
all_players = json.loads(st.secrets["players"])
players = load_json(DATA_FILE)
registration_open = is_registration_open(now)

if is_new_registration_period(now):
    reset_registration()
    players = []
    save_json(DATA_FILE, players)

# ===== ממשק ראשי =====
st.title("🃏💰 טורניר הפוקר השבועי")

# ===== הצגת חיווי על מצב המשחק (רק אם ההרשמה פתוחה) =====
if registration_open:
    st.subheader("📢 מצב נוכחי:")
    if len(players) < MIN_PLAYERS:
        st.warning("⚠️ אין מספיק שחקנים עדיין. אין משחק כרגע.")
    elif len(players) == 5:
        st.info("🚀 יאללה, אתה האחרון לסגור לנו את הפינה!")
    elif len(players) == 7:
        st.info("⏳ תמהר כי נשאר מקום אחרון!")

# ===== הצגת שחקנים רשומים =====
st.subheader("👥 שחקנים רשומים:")
if players:
    for i, p in enumerate(players, start=1):
        st.write(f"{i}. {p['name']}")
else:
    st.info("אין נרשמים עדיין.")

# ===== סטטוס הרשמה =====
if registration_open:
    st.markdown("<div style='background-color:#d4edda;padding:10px;border-radius:5px;color:#155724;'>✅ ההרשמה פתוחה! ניתן להירשם ולהסיר את עצמך.</div>", unsafe_allow_html=True)
else:
    st.markdown("<div style='background-color:#f8d7da;padding:10px;border-radius:5px;color:#721c24;'>❌ ההרשמה סגורה כרגע. תחזור בשישי ב-18:00!</div>", unsafe_allow_html=True)

# ===== טופס פעולה =====
st.markdown("---")
st.header("📊 טופס פעולה")

name = st.text_input("שם משתמש")
code = st.text_input("קוד אישי", type="password")
action = st.radio("בחר פעולה", ["להירשם למשחק", "להסיר את עצמי"])

if st.button("שלח"):
    if not name.strip() or not code.strip():
        st.warning("יש להזין שם וקוד.")
    else:
        allowed_player = get_player(name, all_players)
        existing_player = get_player(name, players)

        if action == "להירשם למשחק":
            if not registration_open:
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
            if not registration_open:
                st.warning("לא ניתן להסיר את עצמך כשההרשמה סגורה.")
            elif existing_player and existing_player["code"] == code:
                players = [p for p in players if p["name"] != name]
                save_json(DATA_FILE, players)
                st.success("הוסרת מהרשימה.")
            else:
                st.error("שם או קוד שגויים.")
