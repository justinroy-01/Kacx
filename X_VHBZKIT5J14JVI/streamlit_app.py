import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd
import time

# 1. Get Session
session = get_active_session()

# Page Config
st.set_page_config(layout="wide", page_title="Kacx Inspector")

# --- NAVIGATION & HEADER ---
# We use columns to put the Title on the left and Buttons on the right
col_header, col_nav1, col_nav2 = st.columns([6, 1, 1])

with col_header:
    st.title("Kacx")
    st.caption("AI-Powered Infrastructure Risk Assessment")

# Initialize Session State for Navigation
if 'page' not in st.session_state:
    st.session_state.page = 'Home'

with col_nav1:
    if st.button("🔍 Find"):
        st.session_state.page = 'Find'

with col_nav2:
    if st.button("➕ Calculate"):
        st.session_state.page = 'Calculate'

st.divider()

# ==========================================
# PAGE 1: CALCULATE (Upload & Analyze)
# ==========================================
if st.session_state.page == 'Calculate':
    st.subheader("New Inspection Entry")
    
    with st.form("inspection_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        
        with c1:
            prop_input = st.text_input("Property ID", placeholder="e.g., HOUSE_005")
            room_input = st.text_input("Room Name", placeholder="e.g., Kitchen")
        
        with c2:
            uploaded_file = st.file_uploader("Upload Defect Image", type=['png', 'jpg', 'jpeg'])
            notes_input = st.text_area("Inspector Notes", placeholder="Describe the issue...")
            
        submitted = st.form_submit_button("🚀 Upload & Calculate Risk")
        
        if submitted and uploaded_file and prop_input:
            # 1. SAVE IMAGE TO STAGE
            # Note: In Streamlit-in-Snowflake, we write the file stream to the stage
            try:
                # Create a unique filename
                file_name = f"upload_{int(time.time())}_{uploaded_file.name}"
                
                # Upload logic using Snowpark
                # We save it to the @HOUSE_IMAGES stage
                session.file.put_stream(uploaded_file, f"@HOUSE_IMAGES/{file_name}", auto_compress=False)
                
                # 2. INSERT RECORD INTO TABLE
                insert_query = f"""
                INSERT INTO INSPECTION_RECORDS (PROPERTY_ID, ROOM_NAME, IMAGE, INSPECTOR_NOTES)
                VALUES ('{prop_input}', '{room_input}', '{file_name}', '{notes_input}')
                """
                session.sql(insert_query).collect()
                st.success("✅ Image uploaded and record saved.")
                
                # 3. TRIGGER AI PROCESSING
                with st.spinner("🤖 AI is analyzing image pixels and notes..."):
                    status = session.sql("CALL PROCESS_INSPECTION_IMAGES()").collect()[0][0]
                
                st.success(f"Analysis Complete: {status}")
                
                # 4. SHOW RESULT IMMEDIATELY
                # We fetch the specific record we just created
                result_df = session.sql(f"""
                    SELECT * FROM V_PROPERTY_RISK_DASHBOARD 
                    WHERE IMAGE = '{file_name}'
                """).to_pandas()
                
                if not result_df.empty:
                    row = result_df.iloc[0]
                    st.info(f"**Verdict:** {row['HAZARD_TYPE']} (Severity: {row['SEVERITY_LEVEL']}/5)")
                    if row['RISK_CATEGORY'] == 'CRITICAL':
                         st.error(f"RISK SCORE: {row['RISK_SCORE']} - CRITICAL ACTION REQUIRED")
                    else:
                         st.write(f"Risk Score: {row['RISK_SCORE']}")
                
            except Exception as e:
                st.error(f"Upload Failed: {str(e)}")

# ==========================================
# PAGE 2: FIND (The Dashboard)
# ==========================================
elif st.session_state.page == 'Find':
    st.subheader("Property Risk Dashboard")
    
    # Sidebar Filter (Only visible on 'Find' page)
    properties = session.sql("SELECT DISTINCT PROPERTY_ID FROM V_PROPERTY_RISK_DASHBOARD ORDER BY PROPERTY_ID").collect()
    if properties:
        prop_id = st.selectbox("Select Property to Inspect", [p['PROPERTY_ID'] for p in properties])
        
        # Fetch Data
        data = session.sql(f"SELECT * FROM V_PROPERTY_RISK_DASHBOARD WHERE PROPERTY_ID = '{prop_id}'").to_pandas()
        
        # Summary Metrics
        total_score = data['RISK_SCORE'].sum()
        c_metric, c_msg = st.columns([1, 3])
        c_metric.metric("Total Risk Score", int(total_score))
        
        with c_msg:
            if total_score > 50:
                st.error(f"🚨 **HIGH RISK PROPERTY** ({int(total_score)} pts)")
            elif total_score > 20:
                st.warning(f"⚠️ **MODERATE RISK** ({int(total_score)} pts)")
            else:
                st.success(f"✅ **LOW RISK** ({int(total_score)} pts)")

        st.divider()

        # Display Gallery
        for index, row in data.iterrows():
            with st.container():
                c1, c2, c3 = st.columns([1, 1, 2])
                with c1:
                    if row['IMAGE_URL']:
                        st.image(row['IMAGE_URL'], use_container_width=True)
                    else:
                        st.caption("No Image")
                with c2:
                    st.write(f"**{row['ROOM_NAME']}**")
                    st.write(f"Type: `{row['HAZARD_TYPE']}`")
                    st.write(f"Severity: {'⭐' * int(row['SEVERITY_LEVEL'])}")
                with c3:
                    st.info(row['INSPECTOR_NOTES'])
                    if row['RISK_CATEGORY'] == 'CRITICAL':
                        st.markdown(":red[**CRITICAL**]")
                st.divider()
    else:
        st.info("No records found. Go to 'Calculate' to add one!")

# ==========================================
# PAGE 3: HOME (Welcome)
# ==========================================
else:
    st.markdown("### Welcome to Kacx")
    st.write("Your AI-powered assistant for automated building inspection and risk scoring.")
    st.write("👈 **Select an option above:**")
    st.markdown("- **Calculate:** Upload a new photo to detect defects instantly.")
    st.markdown("- **Find:** Browse reports for existing properties.")