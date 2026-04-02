import streamlit as st
import requests
import time
import os

st.set_page_config(page_title="BrandSync", page_icon="🎬", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
}

/* Background gradient for main app */
.stApp {
    background: linear-gradient(135deg, #09090E, #1A1A2E);
    color: #FFFFFF;
}

[data-testid="stHeader"] {
    background: rgba(9, 9, 14, 0.8) !important;
    backdrop-filter: blur(10px);
}

[data-testid="stSidebar"] {
    background: rgba(17, 17, 26, 0.95);
    border-right: 1px solid rgba(255, 255, 255, 0.1);
}

div.stButton > button:first-child[data-testid="baseButton-primary"] {
    background: linear-gradient(90deg, #FF007A, #7928CA);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.6rem 2rem;
    font-weight: 600;
    font-size: 1.1rem;
    box-shadow: 0 4px 15px rgba(255, 0, 122, 0.3);
    transition: all 0.3s ease;
    width: 100%;
}

div.stButton > button:first-child[data-testid="baseButton-primary"]:hover {
    box-shadow: 0 6px 20px rgba(121, 40, 202, 0.5);
    transform: translateY(-2px);
    color: white;
}

/* Specific styling for the update button */
div.stButton > button:first-child[data-testid="baseButton-secondary"] {
    background: rgba(255, 255, 255, 0.1);
    box-shadow: none;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    transition: all 0.3s ease;
    color: white;
}
div.stButton > button:first-child[data-testid="baseButton-secondary"]:hover {
    background: rgba(255, 255, 255, 0.2);
    border: 1px solid #00D4FF;
    transform: translateY(-2px);
    color: white;
}

h1 {
    font-size: 3.5rem !important;
    font-weight: 800 !important;
    background: -webkit-linear-gradient(45deg, #FF007A, #00D4FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0rem;
    padding-bottom: 0.5rem;
}

.subtitle {
    font-size: 1.2rem;
    color: #A0A0B0;
    margin-bottom: 2rem;
    font-weight: 300;
}

.stProgress .st-bo {
    background: linear-gradient(90deg, #FF007A, #00D4FF);
}

hr {
    border-color: rgba(255,255,255, 0.1);
}

.stTextInput>div>div>input {
    background-color: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #fff;
    border-radius: 8px;
}
.stTextInput>div>div>input:focus {
    border-color: #00D4FF;
    box-shadow: 0 0 0 1px #00D4FF;
}

.stSelectbox>div>div>div {
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    color: #fff;
}

.stTextArea>div>div>textarea {
    background-color: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #fff;
    border-radius: 8px;
}
.stTextArea>div>div>textarea:focus {
    border-color: #FF007A;
    box-shadow: 0 0 0 1px #FF007A;
}

.feature-box {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 24px;
    height: 100%;
    transition: all 0.3s ease;
}
.feature-box:hover {
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.1);
    transform: translateY(-5px);
}
.feature-icon {
    font-size: 2.5rem;
    margin-bottom: 1rem;
}
.feature-title {
    font-weight: 600;
    font-size: 1.2rem;
    color: #fff;
    margin-bottom: 0.5rem;
}
.feature-desc {
    color: #A0A0B0;
    font-size: 0.95rem;
    line-height: 1.5;
}
</style>
""", unsafe_allow_html=True)

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# --- INITIALIZE STATE ---
if "task_id" not in st.session_state:
    st.session_state.task_id = None
if "status" not in st.session_state:
    st.session_state.status = None
if "contract" not in st.session_state:
    st.session_state.contract = None
if "final_video_url" not in st.session_state:
    st.session_state.final_video_url = None

def generate_ad(url, template):
    with st.spinner("Initializing AI Brain and Scraper..."):
        try:
            res = requests.post(f"{API_BASE_URL}/generate", json={"url": url, "template": template})
            res.raise_for_status()
            data = res.json()
            st.session_state.task_id = data["task_id"]
            st.session_state.status = data["status"]
            st.session_state.contract = None
            st.session_state.final_video_url = None
        except Exception as e:
            st.error(f"Failed to start generation: {e}")

# --- SIDEBAR ---
with st.sidebar:
    # Use standard Streamlit image if URL isn't universally available, or just an emoji
    st.markdown("<h1 style='font-size: 2rem !important; margin-bottom: 0;'>🎬 BrandSync</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #A0A0B0; margin-bottom: 20px; font-size: 0.9rem;'>Input your business details to start the creative process.</p>", unsafe_allow_html=True)
    
    url_input = st.text_input("Business URL", placeholder="https://www.example.com")
    template_input = st.selectbox(
        "Template / Vibe", 
        ["Default (Auto-detect)", "Energetic & Modern", "Calm & Trustworthy", "Cinematic & Epic"]
    )
    
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
    if st.button("Generate Ad ✨", type="primary"):
        if url_input:
            generate_ad(url_input, template_input)
        else:
            st.warning("Please enter a URL.")
            
    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<small style='color: #505060; font-family: sans-serif;'>Powered by Gemini, Nano Banana, Veo, and Lyria.</small>", unsafe_allow_html=True)


# --- MAIN AREA ---
if not st.session_state.task_id:
    # Landing Page State
    st.markdown("<h1>BrandSync Studio</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Automated Multi-Modal Video Ad Generation using Google's State-of-the-Art AI.</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: rgba(0, 212, 255, 0.05); border: 1px solid rgba(0, 212, 255, 0.2); border-left: 4px solid #00D4FF; border-radius: 8px; padding: 24px; margin-bottom: 2rem;">
        <h3 style="color: #00D4FF; font-weight: 600; margin-top: 0; margin-bottom: 1rem;">About BrandSync</h3>
        <p style="color: #A0A0B0; line-height: 1.6; margin-bottom: 1rem;">
            BrandSync was built to democratize high-quality video ad creation. We know that businesses often struggle to create engaging, polished marketing material due to cost and time constraints.
        </p>
        <p style="color: #A0A0B0; line-height: 1.6; margin-bottom: 0;">
            With just a single website URL, BrandSync leverages <b>Google Gemini</b> to analyze a brand's exact identity, tone, and visual style. It then orchestrates state-of-the-art models including <b>Nano Banana</b> (scraping), <b>Google Veo</b> (hyper-realistic video generation), and <b>Google Lyria</b> (professional audio synthesis) to generate a complete, ready-to-publish video campaign in minutes!
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.info("👈 Enter a Business URL in the sidebar to generate your first ad!")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">🧠</div>
            <div class="feature-title">AI Knowledge Extraction</div>
            <div class="feature-desc">Automatically scrapes and analyzes the visual and textual identity from any business URL.</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">🎨</div>
            <div class="feature-title">Smart Style Contract</div>
            <div class="feature-desc">Gemini creates a dynamic creative brief ensuring brand consistency across visuals and audio.</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">🎬</div>
            <div class="feature-title">Multi-modal Synthesis</div>
            <div class="feature-desc">Combines Google Veo (video generation) and Lyria (audio) into a polished final ad.</div>
        </div>
        """, unsafe_allow_html=True)
        
    # st.info("👈 Enter a Business URL in the sidebar to generate your first ad!")

else:
    # Generation State
    st.markdown("<h1>Campaign Studio</h1>", unsafe_allow_html=True)
    
    # Auto-polling and Status Banner
    status_color = "#00D4FF"
    if st.session_state.status == "completed":
        status_color = "#00FF7F"
    elif st.session_state.status == "failed":
        status_color = "#FF3366"
        
    st.markdown(f"**Generation Status:** <span style='color: {status_color}; font-weight: 600; text-transform: uppercase;'>{st.session_state.status}</span>", unsafe_allow_html=True)
    
    if st.session_state.status not in ["completed", "failed"]:
        # Show Progress bar
        status_map = {
            "pending_generation": 10,
            "generating": 50,
            "synthesizing": 85
        }
        progress = status_map.get(st.session_state.status, 0)
        st.progress(progress / 100.0)
        
        time.sleep(2)
        try:
            res = requests.get(f"{API_BASE_URL}/status/{st.session_state.task_id}")
            if res.status_code == 200:
                data = res.json()
                st.session_state.status = data.get("status")
                st.session_state.contract = data.get("style_contract")
                st.session_state.final_video_url = data.get("final_video_url")
                st.rerun()
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to backend server. Is FastAPI running?")
            st.stop()
            
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Layout: Status and Result
    col1, col2 = st.columns([1, 1.2], gap="large")
    
    with col1:
        st.markdown("<h3>💡 Style Contract (The Brain)</h3>", unsafe_allow_html=True)
        if st.session_state.contract:
            with st.container():
                st.json(st.session_state.contract)
        else:
            st.info("Waiting for Gemini to generate the creative brief...")
            
    with col2:
        st.markdown("<h3>🎞️ Synthesized Ad</h3>", unsafe_allow_html=True)
        if st.session_state.status == "completed":
            st.success("✨ Generation Complete! Your ad is ready.")
            video_endpoint = f"{API_BASE_URL}/video/{st.session_state.task_id}?t={time.time()}"
            st.video(video_endpoint)
        elif st.session_state.status == "failed":
            st.error("Generation failed. Please check backend logs.")
        else:
            st.markdown("""
            <div style="background: rgba(255,255,255,0.02); border: 2px dashed rgba(255,255,255,0.1); border-radius: 12px; padding: 40px; text-align: center;">
                <h4 style="color: #A0A0B0;">Generating Visuals & Audio...</h4>
                <p style="color: #606070;">The AI models are currently crafting your ad. This may take a few minutes.</p>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Gemini Live Feedback Loop
    if st.session_state.status == "completed":
        st.markdown("<h3>🎙️ Gemini Live Feedback</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #A0A0B0;'>Want to tweak the ad? Type your feedback below, and Gemini will update the style contract and trigger a partial re-regeneration.</p>", unsafe_allow_html=True)
        
        feedback = st.text_area("Feedback", label_visibility="collapsed", placeholder="e.g., 'Make the background music more upbeat (BPM 140) and change visual style to Neon Cyberpunk'")
        
        # Use columns to align the button nicely
        f_col1, f_col2 = st.columns([3, 1])
        with f_col2:
            if st.button("Update & Re-generate 🔄", use_container_width=True):
                with st.spinner("Processing feedback..."):
                    patch = {}
                    if "upbeat" in feedback.lower():
                        patch["audio_vibe"] = "Upbeat neon"
                        patch["audio_bpm"] = 140
                    if "cyberpunk" in feedback.lower():
                        patch["visual_style"] = "Neon Cyberpunk, glowing, highly detailed"
                    
                    if not patch:
                        patch["visual_style"] = feedback
                        
                    try:
                        res = requests.put(f"{API_BASE_URL}/feedback/{st.session_state.task_id}", json=patch)
                        if res.status_code == 200:
                            st.session_state.status = "pending_generation"
                            st.rerun()
                    except Exception as e:
                        st.error(f"Failed to submit feedback: {e}")
