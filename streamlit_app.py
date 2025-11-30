#!/usr/bin/env python3
"""
Streamlit Web Interface for Pet Roast AI
Upload a pet image and generate a roast video in multiple languages
"""

import streamlit as st
import requests
import time
from PIL import Image
import io
import base64
from pathlib import Path

# Backend API configuration
BACKEND_URL = "http://localhost:8000"
TRANSLATE_ENDPOINT = f"{BACKEND_URL}/api/translate-text"
GENERATE_VIDEO_ENDPOINT = f"{BACKEND_URL}/api/generate-video"
VIDEO_STATUS_ENDPOINT = f"{BACKEND_URL}/api/video-status"
VIDEO_RESULT_ENDPOINT = f"{BACKEND_URL}/api/video-result"
FILTERS_ENDPOINT = f"{BACKEND_URL}/api/banuba-filters"

# Language options
LANGUAGES = {
    "English": "en",
    "Hindi (हिन्दी)": "hi",
    "Bengali (বাংলা)": "bn",
    "Tamil (தமிழ்)": "ta",
    "Telugu (తెలుగు)": "te",
    "Malayalam (മലയാളം)": "ml",
    "Kannada (ಕನ್ನಡ)": "kn",
    "Gujarati (ગુજરાતી)": "gu",
    "Marathi (मराठी)": "mr",
    "Punjabi (ਪੰਜਾਬੀ)": "pa",
    "Odia (ଓଡ଼ିଆ)": "or",
    "Assamese (অসমীয়া)": "as",
    "Urdu (اردو)": "ur",
}


def check_backend_health():
    """Check if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/healthz", timeout=2)
        return response.status_code == 200
    except:
        return False


def translate_text(text, source_lang, target_lang):
    """Translate text using the backend API"""
    try:
        response = requests.post(
            TRANSLATE_ENDPOINT,
            json={
                "text": text,
                "source_lang": source_lang,
                "target_lang": target_lang
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Translation failed: {str(e)}")
        return None


def generate_video(text, image_url):
    """Generate video using the backend API"""
    try:
        response = requests.post(
            GENERATE_VIDEO_ENDPOINT,
            json={
                "text": text,
                "image_url": image_url
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Video generation failed: {str(e)}")
        return None


def get_video_status(job_id):
    """Check video generation status"""
    try:
        response = requests.get(
            f"{VIDEO_STATUS_ENDPOINT}/{job_id}",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Status check failed: {str(e)}")
        return None


def get_video_result(job_id):
    """Get the final video result"""
    try:
        response = requests.get(
            f"{VIDEO_RESULT_ENDPOINT}/{job_id}",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to get video result: {str(e)}")
        return None


def get_ar_filters():
    """Get available AR filters"""
    try:
        response = requests.get(FILTERS_ENDPOINT, timeout=5)
        response.raise_for_status()
        return response.json().get("filters", [])
    except Exception as e:
        st.warning(f"Could not load AR filters: {str(e)}")
        return []


def image_to_base64(image):
    """Convert PIL Image to base64 string"""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/jpeg;base64,{img_str}"


# Streamlit App Configuration
st.set_page_config(
    page_title="Pet Roast AI 🐾",
    page_icon="🐶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1rem 0;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        border: none;
        font-size: 1.1rem;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .status-success {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
    }
    .status-info {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
    }
    .status-warning {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
    }
    .status-error {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# Main Header
st.markdown('<h1 class="main-header">🐾 Pet Roast AI 🎬</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Generate hilarious roast videos of your pets in 12+ Indian languages!</p>', unsafe_allow_html=True)

# Check backend health
if not check_backend_health():
    st.error("⚠️ Backend server is not running! Please start the backend first.")
    st.info("Run: `uvicorn app.main:app --host 0.0.0.0 --port 8000`")
    st.stop()
else:
    st.success("✅ Backend connected successfully!")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")

    # Language selection
    st.subheader("🌐 Language Settings")
    source_language = st.selectbox(
        "Source Language",
        options=list(LANGUAGES.keys()),
        index=0,
        help="Language of your roast text"
    )

    target_language = st.selectbox(
        "Target Language for Translation",
        options=list(LANGUAGES.keys()),
        index=1,
        help="Translate to this language"
    )

    # AR Filters
    st.subheader("🎭 AR Filters")
    filters = get_ar_filters()
    if filters:
        selected_filter = st.selectbox(
            "Choose AR Filter",
            options=["None"] + [f["name"] for f in filters],
            help="Apply AR effects to your pet video"
        )

        if selected_filter != "None":
            filter_info = next(f for f in filters if f["name"] == selected_filter)
            st.info(f"**{filter_info['name']}**: {filter_info['description']}")

    st.divider()

    # About section
    st.subheader("ℹ️ About")
    st.markdown("""
    This app uses:
    - **AI4Bharat IndicTrans2** for translation
    - **Revid.ai** for video generation
    - **FastAPI** backend
    - **Redis** for job persistence
    """)

    st.divider()

    # Stats
    st.subheader("📊 System Info")
    st.metric("Backend Status", "🟢 Online" if check_backend_health() else "🔴 Offline")
    st.metric("Supported Languages", len(LANGUAGES))

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 Step 1: Write Your Roast")

    roast_text = st.text_area(
        "Enter your roast text",
        placeholder="Your dog thinks the vacuum cleaner is a monster...",
        height=150,
        help="Write a funny roast about your pet"
    )

    # Translation test
    if roast_text and st.button("🔄 Translate Text", key="translate_btn"):
        with st.spinner("Translating..."):
            src_lang = LANGUAGES[source_language]
            tgt_lang = LANGUAGES[target_language]

            result = translate_text(roast_text, src_lang, tgt_lang)

            if result:
                st.success("Translation complete!")
                st.markdown("**Original:**")
                st.write(roast_text)
                st.markdown(f"**Translated to {target_language}:**")
                st.write(result.get("translated_text", ""))

with col2:
    st.header("🖼️ Step 2: Upload Pet Image")

    uploaded_file = st.file_uploader(
        "Choose an image of your pet",
        type=["jpg", "jpeg", "png"],
        help="Upload a clear photo of your pet"
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Your Pet", use_column_width=True)

        # Convert image to base64 for API
        image_data_url = image_to_base64(image)

# Video Generation Section
st.divider()
st.header("🎬 Step 3: Generate Video")

col_gen1, col_gen2, col_gen3 = st.columns([1, 1, 1])

with col_gen1:
    st.metric("Roast Text", "✅ Ready" if roast_text else "❌ Missing")

with col_gen2:
    st.metric("Pet Image", "✅ Ready" if uploaded_file else "❌ Missing")

with col_gen3:
    can_generate = bool(roast_text and uploaded_file)
    st.metric("Status", "🚀 Ready to Generate" if can_generate else "⏳ Waiting")

if can_generate:
    if st.button("🎥 Generate Roast Video", key="generate_btn"):
        with st.spinner("Creating your video... This may take a few minutes..."):
            # Generate video
            result = generate_video(roast_text, image_data_url)

            if result:
                job_id = result.get("job_id")
                st.session_state.job_id = job_id
                st.session_state.job_status = result.get("status")

                st.success(f"✅ Video job created! Job ID: `{job_id}`")
                st.info("Status: " + result.get("status", "queued"))

# Video Status Tracking
if "job_id" in st.session_state:
    st.divider()
    st.header("📊 Video Generation Status")

    col_status1, col_status2 = st.columns([2, 1])

    with col_status1:
        st.info(f"Tracking Job ID: `{st.session_state.job_id}`")

    with col_status2:
        if st.button("🔄 Refresh Status"):
            status_result = get_video_status(st.session_state.job_id)
            if status_result:
                st.session_state.job_status = status_result.get("status")
                st.rerun()

    # Status display
    status = st.session_state.get("job_status", "unknown")

    if status == "queued":
        st.markdown('<div class="status-box status-info">⏳ <b>Queued:</b> Your video is in the queue...</div>', unsafe_allow_html=True)
        st.progress(0.25)
    elif status == "processing":
        st.markdown('<div class="status-box status-warning">⚙️ <b>Processing:</b> Generating your video...</div>', unsafe_allow_html=True)
        st.progress(0.5)
    elif status == "completed":
        st.markdown('<div class="status-box status-success">✅ <b>Completed:</b> Your video is ready!</div>', unsafe_allow_html=True)
        st.progress(1.0)

        # Get video result
        if st.button("📥 Get Video Result"):
            video_result = get_video_result(st.session_state.job_id)
            if video_result and video_result.get("video_url"):
                st.success("Video URL:")
                st.code(video_result["video_url"])
                st.markdown(f"[🎬 Watch Video]({video_result['video_url']})")
    elif status == "failed":
        st.markdown('<div class="status-box status-error">❌ <b>Failed:</b> Video generation failed</div>', unsafe_allow_html=True)
        st.error("Please try again or check the backend logs")
    else:
        st.info(f"Current status: {status}")

    # Auto-refresh option
    auto_refresh = st.checkbox("Auto-refresh status every 5 seconds")
    if auto_refresh and status not in ["completed", "failed"]:
        time.sleep(5)
        st.rerun()

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p>Built with ❤️ using FastAPI, IndicTrans2, Revid.ai, and Streamlit</p>
    <p>Supports: English, Hindi, Bengali, Tamil, Telugu, Malayalam, Kannada, Gujarati, Marathi, Punjabi, Odia, Assamese, Urdu</p>
</div>
""", unsafe_allow_html=True)
