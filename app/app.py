import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import numpy as np
import cv2
import os
import io
from datetime import datetime
from tensorflow.keras.models import load_model

# --- CONFIG & MODERN STYLING ---
st.set_page_config(page_title="NeuroScan AI | Precision Oncology", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #e2e8f0; }
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #020617 100%); }
    
    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 2rem;
        margin-bottom: 20px;
    }
    
    .status-active { color: #38bdf8; font-weight: bold; }
    
    /* Animated Title */
    .main-title {
        font-size: 50px;
        font-weight: 700;
        background: linear-gradient(to right, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- CORE FUNCTIONS ---
@st.cache_resource
def get_model():
    try: return load_model("model/unet_model.h5")
    except: return None

model = get_model()

def init_db():
    conn = sqlite3.connect('neuroscan.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS patients 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, doctor TEXT, 
                  name TEXT, age INTEGER, tumor_pct REAL, stage TEXT, date TEXT)''')
    conn.commit()
    conn.close()

def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text): return make_hashes(password) == hashed_text

# --- PAGE: ABOUT ---
def about_section():
    st.markdown("<h1 class='main-title'>NeuroScan AI Insight</h1>", unsafe_allow_html=True)
    
    col_img, col_txt = st.columns([1, 1.2])
    
    with col_img:
        # PATH UPDATE: Looks for the file in the same folder as this script
        process_path = os.path.join(os.path.dirname(__file__), "process_animation.gif")
        
        if os.path.exists(process_path):
            st.image(process_path, caption="AI Voxel Segmentation in Action")
        else:
            # Fallback if the file is missing
            st.warning("Animation 'process_animation.gif' not found in the app folder.")
        
    with col_txt:
        st.markdown("""
        <div class="glass-card">
        🧠  What is a Brain Tumor?
                    
        A brain tumor is a mass or growth of abnormal cells in your brain. Many different types of brain tumors exist. Some brain tumors are noncancerous (benign), and some are cancerous (malignant).
        
        ### ⚠️ Why Early Detection Matters
        The brain is the most complex organ. Even a small growth can apply pressure to sensitive areas, affecting vision, motor skills, and memory. **Early detection increases survival rates by up to 70%**.
        
        ### 🤖 How We Help
        Our system uses a **U-Net Deep Learning Architecture**. It scans every pixel (voxel) of an MRI slice to identify patterns that are invisible to the naked eye.
        1. **Pixel-Level Accuracy:** Highlights exact tumor boundaries.
        2. **Stage Prediction:** Estimates clinical staging based on tissue involvement.
        3. **Automated Archiving:** Securely stores history for longitudinal tracking.
        </div>
        """, unsafe_allow_html=True)

# --- PAGE: LOGIN/REGISTER ---
def login_page():
    left, right = st.columns([1.5, 1])
    with left:
        st.markdown("<h1 style='font-size: 60px;'>Welcome to the <br><span style='color:#38bdf8'>Future of Oncology</span></h1>", unsafe_allow_html=True)
        st.write("Precision diagnostics powered by Advanced Neural Networks.")
        
        # PATH UPDATE: Looks for the file in the same folder as this script
        hero_path = os.path.join(os.path.dirname(__file__), "hero_animation.gif")
        
        if os.path.exists(hero_path):
            st.image(hero_path, width=500)
        else:
            # Fallback if the file is missing
            st.info("Animation 'hero_animation.gif' not found in the app folder.")
        
    with right:
        # Re-enabling the glass card for a cleaner look
        
        #st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        # Use an <h3> tag so the CSS above can find it
        st.markdown("<h3>Access Portal</h3>", unsafe_allow_html=True)
        
        choice = st.radio("Select Action", ["Login", "Register"], label_visibility="collapsed")
        
        username = st.text_input("Medical ID", placeholder="Enter your ID")
        password = st.text_input("Access Key", type='password', placeholder="Enter your key")
        
       
        
        if choice == "Register":
            if st.button("Initialize Account"):
                conn = sqlite3.connect('neuroscan.db')
                c = conn.cursor()
                try:
                    c.execute('INSERT INTO users VALUES (?,?)', (username, make_hashes(password)))
                    conn.commit()
                    st.success("Account Ready. Please Login.")
                except: st.error("ID already registered.")
                conn.close()
        else:
            if st.button("Unlock Dashboard"):
                conn = sqlite3.connect('neuroscan.db')
                c = conn.cursor()
                c.execute('SELECT password FROM users WHERE username = ?', (username,))
                res = c.fetchone()
                if res and check_hashes(password, res[0]):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else: st.error("Invalid Credentials.")
        # ... rest of your login logic ...
        
        st.markdown('</div>', unsafe_allow_html=True)

# --- PAGE: MAIN DASHBOARD ---
def main_app():
    with st.sidebar:
        st.markdown(f"### 👨‍⚕️ Dr. {st.session_state.username}")
        menu = st.radio("Menu", ["Dashboard", "Patient History", "About System"])
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    if menu == "About System":
        about_section()

    elif menu == "Dashboard":
        st.markdown("<h2 class='main-title'>Diagnostic Dashboard</h2>", unsafe_allow_html=True)
        
        with st.form("intake", clear_on_submit=True):
            st.markdown("### 📋 Patient Intake")
            c1, c2 = st.columns(2)
            p_name = c1.text_input("Full Name")
            p_age = c2.number_input("Age", 1, 100)
            p_scan = st.file_uploader("Upload MRI Slice (Axial)", type=['png', 'jpg', 'jpeg'])
            submit = st.form_submit_button("Start AI Segmentation")

        if submit and p_scan and p_name:
            # Image Logic
            file_bytes = np.asarray(bytearray(p_scan.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
            
            # AI Inference
            img_input = cv2.resize(img, (128, 128)) / 255.0
            img_input = img_input.reshape(1, 128, 128, 1)
            
            with st.spinner("🧠 Voxel-wise Analysis..."):
                if model: pred = model.predict(img_input)[0]
                else: pred = np.zeros((128,128,1)) # Fallback
            
            # Overlay
            mask = (pred[:,:,0] > 0.5).astype("uint8") * 255
            mask_res = cv2.resize(mask, (img.shape[1], img.shape[0]))
            img_bgr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            red_l = np.zeros_like(img_bgr); red_l[:,:,2] = mask_res
            res_img = cv2.addWeighted(img_bgr, 0.8, red_l, 0.4, 0)
            
            # Show Results
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            v1, v2 = st.columns(2)
            v1.image(img, caption="Original MRI", use_container_width=True)
            v2.image(res_img, caption="AI Detection Result", use_container_width=True)
            
            t_pct = float(np.mean(pred > 0.5) * 100)
            stage = "Healthy" if t_pct < 0.5 else "Stage I" if t_pct < 10 else "Stage II" if t_pct < 25 else "Stage III"
            
            st.metric("Abnormal Tissue Involvement", f"{t_pct:.2f}%", stage)
            
            # Database Save
            conn = sqlite3.connect('neuroscan.db')
            c = conn.cursor()
            c.execute('INSERT INTO patients (doctor, name, age, tumor_pct, stage, date) VALUES (?,?,?,?,?,?)', 
                      (st.session_state.username, p_name, p_age, t_pct, stage, datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
            
            # Report Generation (Mock CSV/Text for now)
            report_txt = f"Patient: {p_name}\nAge: {p_age}\nDiagnosis: {stage}\nInvolvement: {t_pct:.2f}%\nDate: {datetime.now()}"
            st.download_button("📂 Download Clinical Report", report_txt, file_name=f"{p_name}_Report.txt")
            st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "Patient History":
        st.title("📁 Medical Archives")
        conn = sqlite3.connect('neuroscan.db')
        df = pd.read_sql(f"SELECT name, age, tumor_pct, stage, date FROM patients WHERE doctor='{st.session_state.username}'", conn)
        conn.close()
        st.dataframe(df, use_container_width=True)

# --- INIT ---
init_db()
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()
else:
    main_app()