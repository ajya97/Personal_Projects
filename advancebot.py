import streamlit as st
import pandas as pd
import numpy as np
import random,json
from datetime import datetime
from Crypto.Cipher import AES
import base64
import hashlib

# --------------------------- APP CONFIG ---------------------------
st.set_page_config(page_title="Hospital Data Insight Lab", page_icon="🏥", layout="wide")

# --------------------------- CUSTOM STYLES ---------------------------
st.markdown("""
    <style>
        /* Main title style */
        .main-title {
            text-align: center;
            font-size: 2.5rem;
            font-weight: 700;
            color: #2E8B57;
            margin-bottom: 0.3rem;
        }
        .subtitle {
            text-align: center;
            color: #555;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        /* Section headers */
        .section-header {
            font-size: 1.4rem;
            font-weight: 600;
            margin-top: 1rem;
            color: #1F4E79;
        }
        /* Card style */
        .card {
            background-color: rgba(30, 136, 229, 0.15);
            padding: 1.2rem 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            margin-bottom: 1.5rem;
        }
        /* Scoreboard layout */
        .score-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .metric {
            font-size: 1.2rem;
            color: #333;
        }
        .correct { color: #2E8B57; font-weight: 600; }
        .incorrect { color: #B22222; font-weight: 600; }
        .highlight {
            background-color: #E8F5E9;
            padding: 10px 15px;
            border-radius: 8px;
            border-left: 4px solid #2E8B57;
        }
        /* Question box — dark/light adaptive */
        .question-box {
            background-color: rgba(30, 136, 229, 0.15); /* translucent blue for dark mode */
            color: #fff; /* white text for dark mode */
            padding: 15px 18px;
            border-left: 5px solid #1E88E5;
            border-radius: 10px;
            font-size: 1.1rem;
            font-weight: 500;
            margin-bottom: 10px;
        }

        /* For light mode compatibility */
        [data-theme="light"] .question-box {
            background-color: #eef6fb;
            color: #000;
        }

    </style>
""", unsafe_allow_html=True)

# --------------------------- HEADER ---------------------------
st.markdown("<h1 class='main-title'>🏥 Hospital Data Insight Lab</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Analyze hospital datasets, challenge your pandas skills, and test your data insight abilities!</p>", unsafe_allow_html=True)
st.divider()

# --------------------------- BACKEND DATASET ---------------------------
@st.cache_data
def load_hospital_dataset():
    return pd.read_csv("Hospital_patient_data.csv")

df = load_hospital_dataset()

for col in ['Admission_Date', 'Discharge_Date', 'Follow_Up_Date', 'Next_Appointment']:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
cat_cols = df.select_dtypes(exclude=["number", "datetime"]).columns.tolist()

    # -------------------------- Encode/Decode --------------------------

def encode(data):
    key = st.secrets["KEY"]
    s = json.dumps(data, separators=(',', ':')).encode()
    k, iv = hashlib.sha256(key.encode()).digest(), b'\0'*16
    pad = 16 - len(s) % 16
    enc = AES.new(k, AES.MODE_CBC, iv).encrypt(s + bytes([pad])*pad)
    return base64.urlsafe_b64encode(enc).decode()

def decode(token):
    key = st.secrets["KEY"]
    try:
        k, iv = hashlib.sha256(key.encode()).digest(), b'\0'*16
        d = AES.new(k, AES.MODE_CBC, iv).decrypt(base64.urlsafe_b64decode(token))
        pad_len = d[-1]
        if pad_len < 1 or pad_len > 16:
            raise ValueError("Bad padding")
        return json.loads(d[:-pad_len].decode())
    except Exception:
        return None  # Return None if decryption fails

# --------------------------- USER LOGIN ---------------------------
if "username" not in st.session_state:
    with st.container():
        st.markdown("<h3 style='text-align:center;'>👤 Enter your username to begin</h3>", unsafe_allow_html=True)
        temp_username = st.text_input("Username:", placeholder="e.g., data_pro_07")
        if temp_username:
            st.session_state.username = temp_username
            st.rerun()
else:
    username = st.session_state.username
    user_file = f"{encode(username)}.txt"

    # --------------------------- DATASET DOWNLOAD ---------------------------
    with st.container():
        st.markdown(f"<h3 class='section-header'>💾 Welcome, {username}!</h3>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)

        with c1:
            st.download_button(
                label="📥 Download Hospital Dataset (CSV)",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name='hospital_dataset.csv',
                mime='text/csv',
                use_container_width=True
            )

        # Initialize toggle state (only once)
        if "show_dataset" not in st.session_state:
            st.session_state.show_dataset = False

        with c2:
            toggle_label = "👁️ Hide Hospital Dataset" if st.session_state.show_dataset else "📊 View Hospital Dataset"
            vbtn = st.button(toggle_label, use_container_width=True)

            # Toggle visibility on button click
            if vbtn:
                st.session_state.show_dataset = not st.session_state.show_dataset
                st.rerun()

        # Show dataframe if state is active
        if st.session_state.show_dataset:
            st.dataframe(df, use_container_width=True)

    st.divider()


    # --------------------------- SESSION STATE ---------------------------
    if "difficulty" not in st.session_state:
        st.session_state.difficulty = "Easy"
    if "history" not in st.session_state:
        st.session_state.history = []
    if "score" not in st.session_state:
        st.session_state.score = {"correct": 0, "total": 0}

    # --------------------------- LOAD HISTORY ---------------------------
    try:
        with open(f"History/{user_file}", "r") as f:
            st.session_state.history = decode(f.read())
            if st.session_state.history:
                last = st.session_state.history[-1]["score"]
                st.session_state.score.update(last)
    except FileNotFoundError:
        st.session_state.history = []

    # --------------------------- DIFFICULTY SELECTION ---------------------------
    
    with st.container():
        st.markdown(f"<h3 class='section-header'>🎯 Select Difficulty Level</h3>", unsafe_allow_html=True)
        new_difficulty = st.radio("", ["Easy", "Medium", "Hard"], horizontal=True)
    st.divider()

    # --------------------------- QUESTION GENERATOR ---------------------------
    def generate_single_question(df, difficulty):
        q, ans = None, None
        if difficulty == 'Easy':
            if random.random() < 0.5 and numeric_cols:
                col = random.choice(numeric_cols)
                qtype = random.choice(["mean", "max", "min", "count", "sum", "median", "std"])
                funcs = {
                    "mean": ("📊 Average", df[col].mean()),
                    "max": ("📈 Maximum", df[col].max()),
                    "min": ("📉 Minimum", df[col].min()),
                    "count": ("🔢 Count", df[col].count()),
                    "sum": ("🧮 Sum", df[col].sum()),
                    "median": ("⚖ Median", df[col].median()),
                    "std": ("📏 Standard deviation", df[col].std())
                }
                qtext, val = funcs[qtype]
                q = f"{qtext} of column '{col}'?"
                ans = round(val, 2)
            elif cat_cols:
                col = random.choice(cat_cols)
                qtype = random.choice(["mode", "unique"])
                if qtype == "mode":
                    ans = df[col].mode()[0] if not df[col].mode().empty else "Unknown"
                    q = f"💬 Most common value in '{col}'?"
                else:
                    ans = df[col].nunique()
                    q = f"📦 Unique values count in '{col}'?"
        elif difficulty == "Medium":
            if numeric_cols and cat_cols:
                num_col, cat_col = random.choice(numeric_cols), random.choice(cat_cols)
                top_val = df[cat_col].mode()[0] if not df[cat_col].mode().empty else None
                if random.random() < 0.5:
                    q = f"📊 Average '{num_col}' for '{cat_col}' = '{top_val}'?"
                    ans = round(df[df[cat_col] == top_val][num_col].mean(), 2)
                else:
                    q = f"🔢 Count of records where '{cat_col}' = '{top_val}'?"
                    ans = df[df[cat_col] == top_val].shape[0]
        else:  # Hard
            if "BMI" in df.columns and "Gender" in df.columns:
                q = "⚖ Average BMI by gender?"
                ans = round(df.groupby("Gender")["BMI"].mean().mean(), 2)
            else:
                num_col, cat_col = random.choice(numeric_cols), random.choice(cat_cols)
                top_val = df[cat_col].mode()[0]
                q = f"💡 Average '{num_col}' of patients where '{cat_col}' = '{top_val}'?"
                ans = round(df[df[cat_col] == top_val][num_col].mean(), 2)
        return q, str(ans)

    # --------------------------- LOAD QUESTION ---------------------------
    def generate_question(d,difficulty):
        ques,ans = generate_single_question(d, difficulty)
        for i in st.session_state.history:
            if i["question"] == ques:
                return generate_question(d,difficulty)
        return ques,ans
    if "current_question" not in st.session_state:
        st.session_state.current_question, st.session_state.current_answer = generate_question(df, st.session_state.difficulty)

    if new_difficulty != st.session_state.difficulty:
        st.session_state.difficulty = new_difficulty
        st.session_state.current_question, st.session_state.current_answer = generate_question(df, st.session_state.difficulty)
        st.rerun()

    # --------------------------- SCOREBOARD ---------------------------
    et,mt,ht = 0,0,0 
    ec,mc,hc = 0,0,0
    for h in st.session_state.history: 
        if h["difficulty"] == 'Easy': 
            if h['is_correct']: ec +=1
            et += 1 
        elif h["difficulty"] == 'Medium': 
            if h['is_correct']: mc +=1
            mt += 1 
        else: 
            if h['is_correct']: hc +=1
            ht += 1
    st.markdown("<h3 class='section-header'>🏆 Scoreboard</h3>", unsafe_allow_html=True)
    correct = (ec if st.session_state.difficulty == 'Easy' else (mc if st.session_state.difficulty == 'Medium' else hc))
    total = (et if st.session_state.difficulty == 'Easy' else (mt if st.session_state.difficulty == 'Medium' else ht))
    percent = round(correct / total * 100, 2) if total > 0 else 0

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("✅ Correct", correct)
    with col2: st.metric("❌ Incorrect", total - correct)
    with col3: st.metric("🎯 Accuracy", f"{percent}%")

    st.divider()


    # --------------------------- QUESTION AREA ---------------------------
    st.markdown(f"<div class='question-box'>{st.session_state.current_question}</div>", unsafe_allow_html=True)
    user_answer = st.text_input("Your Answer:", placeholder="Type your answer here...")

    if st.button("Submit Answer", use_container_width=True, type="primary"):
        if not user_answer:
            st.error("Please Enter Your Answer.")
            st.stop()
        st.session_state.score["total"] += 1
        user_clean = str(user_answer).strip().lower()
        correct_clean = str(st.session_state.current_answer).strip().lower()
        is_correct = user_clean in correct_clean or correct_clean in user_clean
        if is_correct:
            st.session_state.score["correct"] += 1

        record = {
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "difficulty": st.session_state.difficulty,
            "question": st.session_state.current_question,
            "your_answer": user_answer,
            "correct_answer": st.session_state.current_answer,
            "is_correct": is_correct,
            "score": dict(st.session_state.score)
        }
        st.session_state.history.append(record)

        with open(f"History/{user_file}", "w") as f:
            data = encode(st.session_state.history)
            f.write(data)

        st.success("✅ Correct!" if is_correct else f"❌ Incorrect! Correct answer: {st.session_state.current_answer}")
        st.session_state.current_question, st.session_state.current_answer = generate_single_question(df, st.session_state.difficulty)
        st.rerun()

    # --------------------------- HISTORY ---------------------------
    if st.session_state.history:
        with st.expander("🧾 View Total Attempts"):
            for rec in reversed(st.session_state.history):
                status_icon = "✅" if rec["is_correct"] else "❌"
                st.markdown(f"<div class='card'><b>Q:</b> {rec['question']} <br><b>Answer:</b> {rec['your_answer']} {status_icon}<br><b>Correct:</b> {rec['correct_answer']}<br><i>Difficulty:</i> {rec['difficulty']}</div>", unsafe_allow_html=True)
