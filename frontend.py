import streamlit as st
import requests
import base64

# ---------------------------------------------------------
# 1. Page Config & Layout (Professional Theme)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Nebula ATS", 
    page_icon="💠", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. Helper Functions (For Logo and Backend Communication)
# ---------------------------------------------------------
def get_base64_image(image_path):
    """Loads a local image and converts it to a base64 string."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def process_analysis(backend_url, job_description, uploaded_files):
    """Sends documents to the FastAPI backend and retrieves results."""
    # Read the files as bytes for the API payload
    files_data = [("files", (file.name, file.read(), "application/pdf")) for file in uploaded_files]
    # Standard form data for the job description text
    data = {"job_description": job_description}
    
    try:
        response = requests.post(backend_url, data=data, files=files_data, timeout=120)
        
        if response.status_code == 200:
            return response.json().get("rankings", [])
        else:
            st.error(f"Backend Error [{response.status_code}]: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Connection Failed: Ensure FastAPI backend is running.")
        return None
    except requests.exceptions.Timeout:
        st.error("Operation Timed Out: The model download took too long or the backend is busy.")
        return None

# ---------------------------------------------------------
# 3. Custom CSS Styles (Glassmorphism, Animations, Fonts)
# ---------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600;700&display=swap');

    /* Global Typography & Deep Space Background */
    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif !important;
    }
    
    .stApp {
        background-color: #030712;
        background-image: 
            radial-gradient(1px 1px at 20px 30px, rgba(255,255,255,0.8), rgba(0,0,0,0)),
            radial-gradient(1px 1px at 50px 160px, rgba(255,255,255,0.6), rgba(0,0,0,0)),
            radial-gradient(1px 1px at 130px 80px, rgba(255,255,255,0.9), rgba(0,0,0,0));
        background-repeat: repeat;
        background-size: 200px 200px;
    }
    
    /* Clean Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(15,23,42,0.8) 0%, rgba(3,7,18,0.9) 100%) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    h1, h2, h3, h4, h5, p, label {
        color: #F8FAFC !important;
    }

    /* Primary Action Button with Animation */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #2563EB 0%, #4F46E5 100%);
        color: white !important;
        border: none;
        border-radius: 6px;
        padding: 12px 28px;
        font-size: 16px;
        font-weight: 600;
        letter-spacing: 1px;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.4);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    div.stButton > button:first-child:hover {
        box-shadow: 0 6px 25px rgba(79, 70, 229, 0.6);
        transform: translateY(-2px);
    }

    /* Animated Result Cards */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .result-card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(12px);
        padding: 24px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-left: 4px solid #4F46E5;
        margin-bottom: 20px;
        animation: fadeInUp 0.6s ease-out forwards;
    }

    /* High-Tech Skill Pills (Matched vs Missing) */
    .skill-pill {
        display: inline-block;
        border-radius: 4px;
        padding: 4px 12px;
        margin: 4px 6px 4px 0;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .pill-match { 
        background-color: rgba(16, 185, 129, 0.1); 
        color: #10B981; 
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .pill-miss { 
        background-color: rgba(239, 68, 68, 0.1); 
        color: #EF4444; 
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    /* Input Area Overrides (Forms) */
    .stTextArea textarea, .stTextInput input {
        background-color: rgba(15, 23, 42, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #4F46E5 !important;
        box-shadow: 0 0 0 1px #4F46E5 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. Custom Header with Local Round Logo Injection
# ---------------------------------------------------------
# Attempt to load your local logo.png from the project folder.
# Falls back to a generic icon if the file is not found.
try:
    # Converts your local logo.png into web-safe code
    img_b64 = get_base64_image("logo.png")
    # THE CIRCULAR FIX: border-radius: 50% makes it round. object-fit: cover forces centering.
    img_html = f'<img src="data:image/png;base64,{img_b64}" style="width: 75px; height: 75px; object-fit: cover; border-radius: 50%; box-shadow: 0px 0px 15px rgba(79,70,229,0.5);">'
except FileNotFoundError:
    # Fallback just in case the image gets moved or named incorrectly.
    st.warning("Warning: logo.png not found in the project directory. Make sure the 'Type' says PNG in File Explorer.")
    img_html = '<img src="https://cdn-icons-png.flaticon.com/512/915/915933.png" width="55" style="filter: drop-shadow(0px 0px 10px rgba(79,70,229,0.8));">'

# Render the final HTML Header layout
st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
        {img_html}
        <h1 style="margin: 0; font-weight: 700; font-size: 2.5rem; background: -webkit-linear-gradient(#fff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Nebula AI Recruiter</h1>
    </div>
    <p style="color: #94A3B8; font-size: 1.1rem; margin-top: -10px;">Enterprise-grade semantic candidate analysis.</p>
    <hr style="border-color: rgba(255,255,255,0.1); margin-bottom: 30px;">
""", unsafe_allow_html=True)
# ---------------------------------------------------------
# 5. Sidebar Configuration
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ System Config")
    backend_url = st.text_input("Backend Endpoint", "http://127.0.0.1:8000/screen")
    st.divider()
    st.caption("Powered by FastAPI & SentenceTransformers")
    st.caption("Zero Trust PDF verification enabled.")

# ---------------------------------------------------------
# 6. Input Section (Columns)
# ---------------------------------------------------------
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("##### 📝 Role Requirements")
    job_description = st.text_area(
        "Paste the complete job description:", 
        height=200, 
        placeholder="e.g., Seeking a senior engineer proficient in Python, FastAPI, and Next.js..."
    )

with col2:
    st.markdown("##### 📄 Candidate Documents")
    # Zero Trust: frontend enforces .pdf extension limit
    uploaded_files = st.file_uploader(
        "Upload resumes (PDF format only):", 
        type=["pdf"], 
        accept_multiple_files=True
    )

# ---------------------------------------------------------
# 7. Action Button
# ---------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
# Symmetrical layout for the button
action_col1, action_col2, action_col3 = st.columns([1, 2, 1])
with action_col2:
    analyze_button = st.button("RUN SEMANTIC SCAN", use_container_width=True)

# ---------------------------------------------------------
# 8. Results Processing
# ---------------------------------------------------------
if analyze_button:
    # 8a. Preliminary validation (frontend)
    if not job_description.strip():
        st.warning("Action required: Please paste a job description.")
    elif not uploaded_files:
        st.warning("Action required: Upload at least one candidate PDF.")
    else:
        # 8b. Show spinner during neural network analysis
        with st.spinner("Initializing neural network analysis..."):
            
            # 8c. Send data to backend function
            results = process_analysis(backend_url, job_description, uploaded_files)
                
            # 8d. Handle successful results display
            if results:
                st.divider()
                st.markdown("### 📊 Alignment Telemetry")
                st.markdown(f"Analyzed {len(results)} profile(s) successfully.")
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Iterate through ranked results and display cards
                for idx, res in enumerate(results):
                    match_score = res.get('match_score', 0)
                    
                    # HTML Card for Filename and Score
                    st.markdown(f"""
                    <div class="result-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h4 style="margin: 0; color: #E2E8F0; font-weight: 600;">{res['filename']}</h4>
                            <h2 style="margin: 0; color: #4F46E5; text-shadow: 0 0 10px rgba(79,70,229,0.4);">{match_score}%</h2>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Native Streamlit progress bar (adds semantic texture)
                    st.progress(match_score / 100)
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Skill Pills (Columns)
                    skill_col1, skill_col2 = st.columns(2)
                    
                    with skill_col1:
                        st.markdown("**✓ Verified Competencies**")
                        if res['matched_skills']:
                            # Generate HTML for GREEN matched skill pills
                            html_matches = "".join([f"<span class='skill-pill pill-match'>{skill}</span>" for skill in res['matched_skills']])
                            st.markdown(html_matches, unsafe_allow_html=True)
                        else:
                            st.caption("No direct signals detected.")
                            
                    with skill_col2:
                        st.markdown("**⚠ Identified Gaps**")
                        if res['missing_skills']:
                            # Generate HTML for RED missing skill pills
                            html_misses = "".join([f"<span class='skill-pill pill-miss'>{skill}</span>" for skill in res['missing_skills']])
                            st.markdown(html_misses, unsafe_allow_html=True)
                        else:
                            st.caption("All required systems nominal.")
                            
                    # Spacing between candidate profiles
                    st.markdown("<br><br>", unsafe_allow_html=True) 
            elif results == []:
                st.warning("Scan complete. No valid results found. (Backend may have rejected file content signature or size).")

# ---------------------------------------------------------
# 9. Global Footer
# ---------------------------------------------------------
st.markdown("""
<div style='text-align: center; margin-top: 60px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.05); color: #64748B; font-size: 13px;'>
    <p>Engineered by Anamika P Anil • 2026 AI Portfolio</p>
    <p>Built with ❤️ using Python, FastAPI, & Streamlit</p>
</div>
""", unsafe_allow_html=True)