import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd
import time
import json
from fpdf import FPDF 

# --- CONFIGURATION ---
session = get_active_session()
st.set_page_config(layout="wide", page_title="Kacx Inspector", initial_sidebar_state="expanded")

# --- DARK THEME CSS ---
st.markdown("""
<style>
    /* Main App Background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #00d4ff !important;
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
    }
    
    /* Cards/Containers */
    .stContainer, div[data-testid="stVerticalBlock"] > div {
        background: rgba(30, 30, 50, 0.7);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(0, 212, 255, 0.3);
        backdrop-filter: blur(10px);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 25px;
        font-weight: bold;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background: rgba(20, 20, 40, 0.8) !important;
        border: 1px solid rgba(0, 212, 255, 0.4) !important;
        border-radius: 8px !important;
        color: #e0e0e0 !important;
    }
    
    /* Select Boxes */
    .stSelectbox > div > div {
        background: rgba(20, 20, 40, 0.8) !important;
        border-radius: 8px !important;
    }
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        color: #00d4ff !important;
        font-size: 2.5rem !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 2px solid rgba(0, 212, 255, 0.3);
    }
    
    /* Dividers */
    hr {
        border-color: rgba(0, 212, 255, 0.3) !important;
    }
    
    /* Success/Warning/Error Messages */
    .stSuccess {
        background: rgba(0, 255, 127, 0.1) !important;
        border-left: 4px solid #00ff7f !important;
    }
    .stWarning {
        background: rgba(255, 193, 7, 0.1) !important;
        border-left: 4px solid #ffc107 !important;
    }
    .stError {
        background: rgba(255, 82, 82, 0.1) !important;
        border-left: 4px solid #ff5252 !important;
    }
    
    /* Images */
    img {
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    }
    
    /* Form Containers */
    .stForm {
        background: rgba(20, 20, 40, 0.6);
        border-radius: 15px;
        padding: 25px;
        border: 1px solid rgba(0, 212, 255, 0.2);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background: rgba(102, 126, 234, 0.2);
        border-radius: 8px;
        color: #00d4ff;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Caption Text */
    .stCaptionContainer, .stCaption {
        color: #a0a0c0 !important;
    }
    
    /* Download Button */
    .stDownloadButton > button {
        background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
    }
    
    /* Chat Popup Styles */
    .chat-popup {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 400px;
        max-height: 600px;
        background: linear-gradient(135deg, rgba(20, 20, 40, 0.98) 0%, rgba(30, 30, 50, 0.98) 100%);
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 212, 255, 0.4);
        border: 2px solid rgba(0, 212, 255, 0.5);
        z-index: 9999;
        display: flex;
        flex-direction: column;
        backdrop-filter: blur(10px);
    }
    
    .chat-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 15px 20px;
        border-radius: 18px 18px 0 0;
        color: white;
        font-weight: bold;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .chat-body {
        flex: 1;
        overflow-y: auto;
        padding: 15px;
        max-height: 400px;
    }
    
    .chat-message {
        margin-bottom: 12px;
        padding: 10px 15px;
        border-radius: 12px;
        max-width: 85%;
        word-wrap: break-word;
    }
    
    .user-message {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: auto;
        text-align: right;
    }
    
    .ai-message {
        background: rgba(0, 212, 255, 0.2);
        color: #e0e0e0;
        border: 1px solid rgba(0, 212, 255, 0.3);
    }
    
    .chat-fab {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.6);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        z-index: 9998;
        transition: all 0.3s;
        border: 2px solid rgba(0, 212, 255, 0.5);
    }
    
    .chat-fab:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 30px rgba(102, 126, 234, 0.8);
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
if 'logged_in_user' not in st.session_state: st.session_state.logged_in_user = None
if 'page' not in st.session_state: st.session_state.page = 'Home'
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'chat_open' not in st.session_state: st.session_state.chat_open = False

# --- PDF CLASS ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Kacx Inspection Report', 0, 1, 'C')
        self.ln(5)
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

# --- HEADER ---
col_header, col_nav1, col_nav2 = st.columns([6, 1, 1])
with col_header:
    st.markdown('<h1 style="font-size: 3rem; margin-bottom: 0;">🏗️ Kacx</h1>', unsafe_allow_html=True)
    st.caption("AI-Powered Infrastructure Risk Assessment")

# --- AUTH FUNCTIONS ---
def attempt_login(uid, password):
    try:
        check = session.sql(f"SELECT FULL_NAME FROM USERS WHERE USER_ID = '{uid}' AND PASSWORD = '{password}'").collect()
        if check:
            st.session_state.logged_in_user = uid
            st.session_state.user_name = check[0]['FULL_NAME']
            st.success("Logged in!"); st.rerun()
        else: st.error("Invalid ID or Password")
    except Exception as e: st.error(f"Login Error: {e}")

def attempt_register(uid, name, password):
    if uid and name and password:
        try:
            session.sql(f"INSERT INTO USERS (USER_ID, FULL_NAME, PASSWORD) VALUES ('{uid}', '{name}', '{password}')").collect()
            st.success("User Created! Please Login.")
        except Exception as e: st.error(f"Error: {e}")
    else: st.warning("All fields required.")

# --- SIDEBAR ---
st.sidebar.title("🔐 Access Control")

if st.session_state.logged_in_user is None:
    st.sidebar.caption("Quick Access")
    tab1, tab2 = st.sidebar.tabs(["Login", "Register"])
    with tab1:
        with st.form("sidebar_login"):
            s_uid = st.text_input("User ID", key="s_uid")
            s_pass = st.text_input("Password", type="password", key="s_pass")
            if st.form_submit_button("Login"): attempt_login(s_uid, s_pass)
    with tab2:
        with st.form("sidebar_register"):
            s_n_uid = st.text_input("New User ID", key="s_n_uid")
            s_n_name = st.text_input("Full Name", key="s_n_name")
            s_n_pass = st.text_input("Password", type="password", key="s_n_pass")
            if st.form_submit_button("Register"): attempt_register(s_n_uid, s_n_name, s_n_pass)
else:
    # LOGGED IN SIDEBAR
    st.sidebar.success(f"👤 {st.session_state.user_name}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in_user = None; st.session_state.page = 'Home'; st.rerun()
    
    st.sidebar.divider()
    
    # --- GLOBAL REPORT GENERATOR (IN SIDEBAR) ---
    st.sidebar.subheader("📄 Report Generator")
    report_prop_id = st.sidebar.text_input("Property ID for PDF", placeholder="e.g., HOUSE_005")
    
    if report_prop_id:
        # Check if data exists
        check_data = session.sql(f"SELECT COUNT(*) FROM V_PROPERTY_RISK_DASHBOARD WHERE PROPERTY_ID = '{report_prop_id}'").collect()[0][0]
        
        if check_data > 0:
            if st.sidebar.button("Generate PDF Now"):
                # Fetch Data
                data = session.sql(f"SELECT * FROM V_PROPERTY_RISK_DASHBOARD WHERE PROPERTY_ID = '{report_prop_id}'").to_pandas()
                
                # Build PDF
                pdf = PDF()
                pdf.add_page()
                
                # Stats
                total_risk = data['RISK_SCORE'].sum()
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, f"Property ID: {report_prop_id}", 0, 1)
                pdf.set_font("Arial", '', 12)
                pdf.cell(0, 10, f"Total Risk Score: {int(total_risk)}", 0, 1)
                pdf.cell(0, 10, f"Generated By: {st.session_state.user_name}", 0, 1)
                pdf.ln(5)
                
                # Headers
                pdf.set_fill_color(220, 220, 220)
                pdf.set_font("Arial", 'B', 10)
                pdf.cell(30, 10, "Room", 1, 0, 'C', 1)
                pdf.cell(40, 10, "Hazard", 1, 0, 'C', 1)
                pdf.cell(20, 10, "Score", 1, 0, 'C', 1)
                pdf.cell(100, 10, "Details", 1, 1, 'C', 1)
                
                # Rows
                pdf.set_font("Arial", '', 9)
                for i, row in data.iterrows():
                    pdf.cell(30, 10, str(row['ROOM_NAME'])[:15], 1)
                    pdf.cell(40, 10, str(row['HAZARD_TYPE'])[:20], 1)
                    pdf.cell(20, 10, f"{row['SEVERITY_LEVEL']}/5", 1, 0, 'C')
                    
                    # Clean Summary Text
                    raw_summary = row['AI_SUMMARY'] if row['AI_SUMMARY'] else row['INSPECTOR_NOTES']
                    summary_text = raw_summary[:60] + "..." if len(raw_summary) > 60 else raw_summary
                    
                    # Add Link if Image Exists
                    if row['IMAGE_URL']:
                        pdf.set_text_color(0, 0, 255)
                        pdf.cell(100, 10, summary_text, 1, 1, 'L', link=row['IMAGE_URL'])
                        pdf.set_text_color(0, 0, 0)
                    else:
                        pdf.cell(100, 10, summary_text, 1, 1, 'L')
                
                # Output to bytes
                pdf_bytes = pdf.output(dest='S').encode('latin-1')
                
                # Show Download Button
                st.sidebar.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_bytes,
                    file_name=f"Report_{report_prop_id}.pdf",
                    mime="application/pdf"
                )
        else:
            st.sidebar.warning("No records found.")

    # --- TOP NAVIGATION ---
    with col_nav1: 
        if st.button("🔍 Find"): st.session_state.page = 'Find'
    with col_nav2: 
        if st.button("➕ Calculate"): st.session_state.page = 'Calculate'

st.divider()

# ==========================================
# PAGE 1: CALCULATE
# ==========================================
if st.session_state.page == 'Calculate':
    if not st.session_state.logged_in_user: st.warning("🔒 Please Login."); st.stop()

    st.subheader(f"New Inspection Entry")
    
    # 1. Select Input Method
    input_method = st.radio("Input Method:", ["📁 Upload Photo", "📸 Take Photo"], horizontal=True)
    
    with st.form("inspection_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            prop_input = st.text_input("Property ID", placeholder="e.g., HOUSE_005")
            room_input = st.text_input("Room Name", placeholder="e.g., Kitchen")
        
        with c2:
            notes_input = st.text_area("Notes", placeholder="Describe the issue...")
            
            # Dynamic Widget based on selection
            img_file = None
            if input_method == "📁 Upload Photo":
                img_file = st.file_uploader("Choose File", type=['png', 'jpg', 'jpeg'])
            else:
                img_file = st.camera_input("Snap Picture")

        submitted = st.form_submit_button("🚀 Upload & Calculate")
        
        if submitted:
            if not (prop_input and room_input and img_file and notes_input):
                st.error("⚠️ All fields are required!")
                st.stop()

            try:
                # Handle filename
                timestamp = int(time.time())
                original_name = img_file.name if hasattr(img_file, 'name') else "camera_capture.jpg"
                file_name = f"upload_{timestamp}_{original_name}"

                # 1. Upload to Stage
                session.file.put_stream(img_file, f"@HOUSE_IMAGES/{file_name}", auto_compress=False)
                
                # 2. Gatekeeper Check
                with st.spinner("🕵️ AI Gatekeeper verifying..."):
                    file_url = session.sql(f"SELECT GET_PRESIGNED_URL(@HOUSE_IMAGES, '{file_name}')").collect()[0][0]
                    gatekeeper_prompt = [{"role": "user", "content": [{"type": "text", "text": "Is this building/construction related? Yes/No"}, {"type": "image_url", "image_url": file_url}]}]
                    is_valid = session.sql("SELECT SNOWFLAKE.CORTEX.COMPLETE('claude-3-5-sonnet', ?)", params=[json.dumps(gatekeeper_prompt)]).collect()[0][0]
                
                if "YES" in is_valid.upper():
                    st.success("✅ Verification Passed!")
                    
                    # 3. Save Record
                    insert_query = f"""
                    INSERT INTO INSPECTION_RECORDS (PROPERTY_ID, ROOM_NAME, IMAGE, INSPECTOR_NOTES, USER_ID)
                    VALUES ('{prop_input}', '{room_input}', '{file_name}', '{notes_input}', '{st.session_state.logged_in_user}')
                    """
                    session.sql(insert_query).collect()
                    
                    # 4. Process
                    with st.spinner("🤖 AI Inspector analyzing..."):
                        session.sql("CALL PROCESS_INSPECTION_IMAGES()").collect()
                    
                    # 5. Show Result
                    result_df = session.sql(f"SELECT * FROM V_PROPERTY_RISK_DASHBOARD WHERE IMAGE = '{file_name}'").to_pandas()
                    if not result_df.empty:
                        row = result_df.iloc[0]
                        st.info(f"Verdict: {row['HAZARD_TYPE']} | Score: {row['RISK_SCORE']}")
                        if row['AI_SUMMARY']:
                            st.write(f"**AI Analysis:** {row['AI_SUMMARY']}")
                else:
                    st.error("⛔ Image Rejected: Not infrastructure related.")

            except Exception as e:
                st.error(f"Error: {str(e)}")

# ==========================================
# PAGE 2: FIND (DASHBOARD)
# ==========================================
elif st.session_state.page == 'Find':
    if not st.session_state.logged_in_user: st.warning("🔒 Please Login."); st.stop()

    st.subheader("Property Risk Dashboard")
    filter_user = st.checkbox("Show only MY inspections", value=True)
    
    query = "SELECT * FROM V_PROPERTY_RISK_DASHBOARD"
    if filter_user:
        query = f"SELECT v.* FROM V_PROPERTY_RISK_DASHBOARD v JOIN INSPECTION_RECORDS r ON v.IMAGE = r.IMAGE WHERE r.USER_ID = '{st.session_state.logged_in_user}'"
    
    properties = session.sql(f"SELECT DISTINCT PROPERTY_ID FROM ({query})").collect()
    
    if properties:
        prop_id = st.selectbox("Select Property", [p['PROPERTY_ID'] for p in properties])
        final_sql = f"SELECT * FROM ({query}) WHERE PROPERTY_ID = '{prop_id}'"
        data = session.sql(final_sql).to_pandas()
        
        if not data.empty:
            total_score = data['RISK_SCORE'].sum()
            c_metric, c_msg = st.columns([1, 3])
            c_metric.metric("Total Risk Score", int(total_score))
            with c_msg:
                if total_score > 50: st.error(f"🚨 **HIGH RISK** ({int(total_score)} pts)")
                elif total_score > 20: st.warning(f"⚠️ **MODERATE RISK** ({int(total_score)} pts)")
                else: st.success(f"✅ **LOW RISK** ({int(total_score)} pts)")
            st.divider()

            for i, row in data.iterrows():
                with st.container():
                    c1, c2, c3 = st.columns([1, 1, 2])
                    with c1: 
                        if row['IMAGE_URL']: st.image(row['IMAGE_URL'], use_container_width=True)
                        st.write(f"**Severity:** {'⭐' * int(row['SEVERITY_LEVEL'])} ({row['SEVERITY_LEVEL']}/5)")
                    with c2:
                        st.write(f"**Room:** {row['ROOM_NAME']}")
                        st.write(f"**Type:** `{row['HAZARD_TYPE']}`")
                        st.caption(f"Inspector Note: {row['INSPECTOR_NOTES']}")
                    with c3:
                        st.markdown("### 🤖 AI Analysis") 
                        if row['AI_SUMMARY']: st.info(row['AI_SUMMARY'])
                        else: st.caption("No summary available.")
                        if row['RISK_CATEGORY'] == 'CRITICAL': st.markdown(":red[**CRITICAL RISK**]")
                    st.divider()
        else: st.info("No records.")
    else: st.info("No records.")

# ==========================================
# PAGE 3: HOME
# ==========================================
else:
    if st.session_state.logged_in_user:
        st.markdown(f"### Welcome back, {st.session_state.user_name}! 👋")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🚀 Start New Inspection", use_container_width=True): st.session_state.page = 'Calculate'; st.rerun()
        with c2:
            if st.button("📊 View Past Reports", use_container_width=True): st.session_state.page = 'Find'; st.rerun()
    else:
        st.markdown("### Welcome to Kacx"); st.write("Your AI-powered assistant.")
        main_tab1, main_tab2 = st.tabs(["🔑 **Login**", "📝 **Register**"])
        with main_tab1:
            with st.form("home_login"):
                h_uid = st.text_input("User ID", key="h_uid")
                h_pass = st.text_input("Password", type="password", key="h_pass")
                if st.form_submit_button("Login Now", type="primary"): attempt_login(h_uid, h_pass)
        with main_tab2:
            with st.form("home_register"):
                h_n_uid = st.text_input("New User ID", key="h_n_uid")
                h_n_name = st.text_input("Full Name", key="h_n_name")
                h_n_pass = st.text_input("Set Password", type="password", key="h_n_pass")
                if st.form_submit_button("Create Account"): attempt_register(h_n_uid, h_n_name, h_n_pass)

# ==========================================
# AI CHAT ASSISTANT (Only if logged in)
# ==========================================
if st.session_state.logged_in_user:
    st.divider()
    
    # Chat Toggle Button
    chat_col1, chat_col2 = st.columns([5, 1])
    with chat_col1:
        st.markdown("### 💬 AI Assistant (മലയാളം/English)")
    with chat_col2:
        if st.session_state.chat_open:
            if st.button("Close ✖", key="close_chat_btn"):
                st.session_state.chat_open = False
                st.rerun()
        else:
            if st.button("Open 💬", key="open_chat_btn"):
                st.session_state.chat_open = True
                st.rerun()
    
    # Chat Interface (Only when open)
    if st.session_state.chat_open:
        with st.container():
            st.markdown("""
                <div style="
                    background: linear-gradient(135deg, rgba(20, 20, 40, 0.95) 0%, rgba(30, 30, 50, 0.95) 100%);
                    border-radius: 15px;
                    padding: 20px;
                    border: 2px solid rgba(0, 212, 255, 0.5);
                    box-shadow: 0 4px 20px rgba(0, 212, 255, 0.3);
                    backdrop-filter: blur(10px);
                    margin-bottom: 20px;
                ">
                    <p style="color: #a0a0c0; margin: 0;">Ask me anything about Kacx Inspector, risk scores, or inspections!</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Chat History Display
            if st.session_state.chat_history:
                for msg in st.session_state.chat_history:
                    if msg['role'] == 'user':
                        st.markdown(f"""
                            <div style="
                                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                                color: white;
                                padding: 12px 18px;
                                border-radius: 15px;
                                margin: 10px 0;
                                margin-left: 20%;
                                text-align: right;
                                box-shadow: 0 2px 10px rgba(102, 126, 234, 0.4);
                            ">
                                <strong>👤 You:</strong> {msg["content"]}
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div style="
                                background: rgba(0, 212, 255, 0.15);
                                color: #e0e0e0;
                                padding: 12px 18px;
                                border-radius: 15px;
                                margin: 10px 0;
                                margin-right: 20%;
                                border: 1px solid rgba(0, 212, 255, 0.3);
                                box-shadow: 0 2px 10px rgba(0, 212, 255, 0.2);
                            ">
                                <strong>🤖 Kacx AI:</strong> {msg["content"]}
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("നമസ്കാരം! / Hello! How can I help you today?")
            
            # Chat Input Form
            with st.form("chat_input_form", clear_on_submit=True):
                col_input, col_send, col_clear = st.columns([6, 1, 1])
                
                with col_input:
                    user_input = st.text_input(
                        "Message", 
                        placeholder="Type in English or Malayalam...", 
                        label_visibility="collapsed"
                    )
                
                with col_send:
                    send_btn = st.form_submit_button("📤", use_container_width=True)
                
                with col_clear:
                    clear_btn = st.form_submit_button("🗑️", use_container_width=True)
                
                if send_btn and user_input:
                    # Add user message
                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    
                    # Prepare AI prompt
                    system_context = f"""You are Kacx AI Assistant, a helpful multilingual chatbot (English & Malayalam).
                    Current User: {st.session_state.user_name}
                    Platform: Property inspection and risk assessment system.
                    
                    Guidelines:
                    - Detect the user's language and respond in the same language
                    - If user writes in Malayalam, respond in Malayalam
                    - Help with questions about inspections, risk scores, reports, and features
                    - Keep responses concise (2-4 sentences)
                    - Be friendly and professional
                    """
                    
                    try:
                        # Call AI model
                        ai_prompt = f"{system_context}\n\nUser Question: {user_input}\n\nAssistant:"
                        ai_response = session.sql(
                            "SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-large2', ?)",
                            params=[ai_prompt]
                        ).collect()[0][0]
                        
                        # Add AI response
                        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                        
                    except Exception as e:
                        st.session_state.chat_history.append({
                            "role": "assistant", 
                            "content": f"Sorry, I encountered an error: {str(e)}"
                        })
                    
                    st.rerun()
                
                if clear_btn:
                    st.session_state.chat_history = []
                    st.success("Chat history cleared!")
                    st.rerun()
