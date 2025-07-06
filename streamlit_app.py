import streamlit as st
import os
from groq import Groq
import PyPDF2
from PIL import Image
import io

# OCR Setup - EasyOCR only
EASYOCR_AVAILABLE = False
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    pass

# Page config
st.set_page_config(
    page_title="Resume Destroyer 🔥",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://github.com/divython/resume_roaster_app',
        'Report a bug': "https://github.com/divython/resume_roaster_app/issues",
        'About': "# Resume Destroyer 🔥\nUpload your resume and prepare for total annihilation!"
    }
)

# Custom CSS with dark theme and advanced UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');
    .stApp { background: linear-gradient(135deg, #0c0c0c 0%, #1a1a1a 25%, #0d1421 50%, #1a1a1a 75%, #0c0c0c 100%) !important; background-attachment: fixed !important; color: #e0e0e0 !important; }
    * { color: #e0e0e0 !important; }
    .main .block-container { background: rgba(13, 20, 33, 0.7); backdrop-filter: blur(10px); border-radius: 20px; padding: 2rem; margin-top: 1rem; box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.1); }
    .main-header { font-family: 'Orbitron', sans-serif; font-size: 4.8rem; font-weight: 900; text-align: center; color: #e0e0e0; margin-bottom: 1rem; letter-spacing: 4px; text-transform: uppercase; text-shadow: 0 0 20px rgba(255, 23, 68, 0.8); }
    .subtitle { font-family: 'Inter', sans-serif; font-size: 1.8rem; text-align: center; color: #e0e0e0; margin-bottom: 3rem; font-weight: 300; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.7); }
    .stButton > button { background: linear-gradient(45deg, #FF1744, #D50000, #8B0000, #B71C1C) !important; color: white !important; border: none !important; padding: 1.5rem 3rem !important; border-radius: 50px !important; font-weight: 900 !important; font-size: 1.2rem !important; font-family: 'Orbitron', sans-serif !important; text-transform: uppercase !important; letter-spacing: 2px !important; box-shadow: 0 10px 30px rgba(255, 23, 68, 0.4) !important; transition: all 0.3s ease !important; width: 100% !important; margin: 1rem 0 !important; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5) !important; }
    .stButton > button:hover { transform: translateY(-3px) scale(1.05) !important; box-shadow: 0 15px 40px rgba(255, 23, 68, 0.6) !important; filter: brightness(1.2) !important; }
    .processing-indicator { display: inline-flex; align-items: center; gap: 8px; font-family: 'Inter', sans-serif; font-weight: 500; margin-bottom: 1rem; }
    .speed-badge { padding: 6px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .speed-fast { background: linear-gradient(45deg, #4CAF50, #8BC34A); color: white; box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3); }
    .speed-normal { background: linear-gradient(45deg, #FF9800, #FFC107); color: white; box-shadow: 0 2px 8px rgba(255, 152, 0, 0.3); }
    .speed-slow { background: linear-gradient(45deg, #F44336, #E91E63); color: white; box-shadow: 0 2px 8px rgba(244, 67, 54, 0.3); }
    .stFileUploader { background: linear-gradient(135deg, #1a1a2e, #16213e); border: 2px dashed rgba(255, 23, 68, 0.3); border-radius: 20px; padding: 2rem; text-align: center; transition: all 0.3s ease; }
    .stFileUploader:hover { border-color: rgba(255, 23, 68, 0.8); background: linear-gradient(135deg, #2a2a3e, #1e2a3e); }
    .stTextArea > div > div > textarea { background: linear-gradient(135deg, #1a1a2e, #16213e) !important; border: 2px solid rgba(255, 255, 255, 0.1) !important; border-radius: 15px !important; padding: 1.5rem !important; font-family: 'Inter', sans-serif !important; color: #e0e0e0 !important; font-size: 1rem !important; line-height: 1.6 !important; }
    .stTextArea > div > div > textarea:focus { border-color: rgba(255, 23, 68, 0.8) !important; box-shadow: 0 0 0 3px rgba(255, 23, 68, 0.1) !important; }
    .roast-container { background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 20%, #16213e 40%, #2c1810 60%, #533483 80%, #6A0572 100%); padding: 3rem; border-radius: 25px; margin: 2rem 0; color: #ffffff; box-shadow: 0 25px 50px rgba(0, 0, 0, 0.6), 0 0 100px rgba(156, 39, 176, 0.3); border: 3px solid; border-image: linear-gradient(45deg, #9C27B0, #673AB7, #3F51B5, #2196F3, #9C27B0) 1; }
    .roast-container h3 { font-family: 'Orbitron', sans-serif; font-size: 2.4rem; font-weight: 700; margin-bottom: 2rem; text-align: center; color: #ffffff !important; letter-spacing: 3px; text-transform: uppercase; text-shadow: 0 0 20px rgba(156, 39, 176, 0.8); }
    .roast-container p { font-size: 1.15rem; line-height: 1.7; font-family: 'Inter', sans-serif; color: #ffffff !important; }
    .brutality-section { background: linear-gradient(135deg, rgba(26, 26, 46, 0.3), rgba(22, 33, 62, 0.3)); border-radius: 20px; padding: 2rem; margin: 2rem 0; border: 2px solid rgba(255, 23, 68, 0.2); box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3); }
    .stSuccess { background: linear-gradient(135deg, rgba(76, 175, 80, 0.2), rgba(139, 195, 74, 0.2)) !important; border-left: 4px solid #4CAF50 !important; border-radius: 10px !important; color: #ffffff !important; font-weight: 600 !important; }
    .stError { background: linear-gradient(135deg, rgba(244, 67, 54, 0.2), rgba(233, 30, 99, 0.2)) !important; border-left: 4px solid #F44336 !important; border-radius: 10px !important; color: #ffffff !important; font-weight: 600 !important; }
    .stInfo { background: linear-gradient(135deg, rgba(33, 150, 243, 0.2), rgba(30, 136, 229, 0.2)) !important; border-left: 4px solid #2196F3 !important; border-radius: 10px !important; color: #ffffff !important; font-weight: 600 !important; }
    .stWarning { background: linear-gradient(135deg, rgba(255, 152, 0, 0.2), rgba(255, 193, 7, 0.2)) !important; border-left: 4px solid #FF9800 !important; border-radius: 10px !important; color: #ffffff !important; font-weight: 600 !important; }
    .streamlit-expanderHeader { background: linear-gradient(135deg, #1a1a2e, #16213e) !important; border-radius: 15px !important; font-weight: 600 !important; color: #ffffff !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; }
    .streamlit-expanderContent { background: linear-gradient(135deg, #0f1419, #1a1a2e) !important; border-radius: 0 0 15px 15px !important; border: 1px solid rgba(255, 255, 255, 0.05) !important; border-top: none !important; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    @media (max-width: 768px) { .main-header { font-size: 3rem; } .stButton > button { font-size: 1rem; padding: 1rem 2rem; } }
</style>
""", unsafe_allow_html=True)

# Initialize Groq client
@st.cache_resource
def get_groq_client():
    api_key = None
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except (KeyError, FileNotFoundError):
        api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        st.error("⚠️ GROQ_API_KEY not found! Set it in Streamlit secrets.")
        st.stop()
    try:
        client = Groq(api_key=api_key)
        return client
    except Exception as e:
        st.error(f"❌ Failed to initialize Groq client: {str(e)}")
        st.stop()

def extract_text_from_pdf(pdf_file):
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""

@st.cache_resource
def get_ocr_reader():
    if EASYOCR_AVAILABLE:
        try:
            return easyocr.Reader(['en'], gpu=False)
        except Exception:
            return None
    return None

def extract_text_from_image(image_file):
    if not EASYOCR_AVAILABLE:
        return ""
    try:
        image = Image.open(image_file)
        reader = get_ocr_reader()
        if reader is None:
            return ""
        import numpy as np
        image_array = np.array(image)
        result = reader.readtext(image_array)
        text = ' '.join([item[1] for item in result])
        return text.strip()
    except Exception:
        return ""

def generate_roast(client, resume_text, roast_type):
    prompts = {
        "devastatingly_brutal": f"DESTROY this pathetic excuse for a resume with absolutely no mercy. This is the most worthless piece of garbage I've ever seen. Point out every single catastrophic failure, every embarrassing weakness, every reason why this person is completely unemployable. Be savage, ruthless, and devastating. Make them question their entire existence and career choices. Show zero compassion - this resume deserves to be completely annihilated.\n\nResume: {resume_text}",
        "soul_crushing": f"OBLITERATE this resume so thoroughly that it makes the reader cry. This is beyond pathetic - it's a complete disaster that represents everything wrong with modern job seekers. Tear apart every single word, every formatting choice, every career decision. Be so brutally honest and savage that it crushes their soul and makes them want to hide under a rock. This person should be ashamed for even thinking about applying for a job with this abomination. Destroy their confidence completely.\n\nResume: {resume_text}"
    }
    system_prompts = {
        "devastatingly_brutal": "You are the most ruthless, savage resume critic in existence. Your job is to completely annihilate resumes with devastating brutality. Show absolutely no mercy, give zero encouragement, and focus only on destroying the person's confidence. Be harsh, savage, and merciless.",
        "soul_crushing": "You are a soul-crushing resume destroyer whose words can make people cry. Your feedback is so brutally honest and devastating that it breaks people's spirits. Be absolutely merciless, savage, and cruel. Make them regret ever writing a resume."
    }
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompts[roast_type]},
                {"role": "user", "content": prompts[roast_type]}
            ],
            model="llama3-8b-8192",
            temperature=0.9,
            max_tokens=1500,
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating roast: {str(e)}")
        return ""

def main():
    if 'resume_text' not in st.session_state:
        st.session_state.resume_text = ""
    if 'roast_type' not in st.session_state:
        st.session_state.roast_type = None
    st.markdown('<div class="main-header">🔥 RESUME DESTROYER 🔥</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Upload your resume and prepare for total annihilation 💀⚡</div>', unsafe_allow_html=True)
    client = get_groq_client()
    st.markdown("### 📄 Upload Your Resume")
    st.markdown("Choose your preferred method to upload your resume:")
    tab1, tab2, tab3 = st.tabs(["📝 Text Input", "📄 PDF Upload", "🖼️ Image Upload"])
    with tab1:
        st.markdown("""
        <div class="processing-indicator">
        📝 <strong>Text Input</strong> 
        <span class="speed-badge speed-fast">⚡ INSTANT</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("**Copy and paste your resume text:**")
        text_input = st.text_area(
            "Resume text:",
            value=st.session_state.resume_text,
            height=300,
            placeholder="Copy and paste your resume text here for complete destruction...",
            label_visibility="collapsed",
            key="text_input_area"
        )
        if text_input != st.session_state.resume_text:
            st.session_state.resume_text = text_input.strip()
            if st.session_state.resume_text:
                st.success("✅ Resume text loaded successfully!")
    with tab2:
        st.markdown("""
        <div class="processing-indicator">
        📄 <strong>PDF Upload</strong> 
        <span class="speed-badge speed-normal">🔄 NORMAL</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("**Upload your resume as PDF:**")
        pdf_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload your resume in PDF format",
            key="pdf_uploader"
        )
        if pdf_file is not None:
            with st.spinner("📄 Processing PDF..."):
                extracted_text = extract_text_from_pdf(pdf_file)
            if extracted_text and extracted_text.strip():
                st.session_state.resume_text = extracted_text.strip()
                st.success(f"✅ PDF processed successfully! Extracted {len(extracted_text)} characters.")
            else:
                st.error("❌ Could not extract text from PDF")
    with tab3:
        st.markdown("""
        <div class="processing-indicator">
        🖼️ <strong>Image Upload</strong> 
        <span class="speed-badge speed-slow">🐌 SLOW</span>
        </div>
        """, unsafe_allow_html=True)
        if not EASYOCR_AVAILABLE:
            st.warning("⚠️ Image processing not available. Please use Text Input or PDF upload.")
        else:
            st.info("💡 Image processing uses AI OCR and may take 10-30 seconds")
        st.markdown("**Upload your resume as image:**")
        image_file = st.file_uploader(
            "Choose an image file",
            type=['png', 'jpg', 'jpeg'],
            help="Upload your resume as an image (PNG, JPG, JPEG)",
            key="image_uploader"
        )
        if image_file is not None:
            st.image(image_file, caption="Your Resume", use_container_width=True)
            if EASYOCR_AVAILABLE:
                with st.spinner("🔍 Reading your resume with AI OCR..."):
                    extracted_text = extract_text_from_image(image_file)
                if extracted_text and extracted_text.strip():
                    st.session_state.resume_text = extracted_text.strip()
                    st.success(f"✅ Image processed successfully! Extracted {len(extracted_text)} characters.")
                else:
                    st.error("❌ Could not extract text from image")
                    st.info("💡 Try using a clearer image or switch to Text Input/PDF upload")
    if st.session_state.resume_text and st.session_state.resume_text.strip():
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown("### 📖 Resume Preview")
        with col2:
            if st.button("🗑️ Clear Resume", key="clear_resume", help="Clear the current resume and start over"):
                st.session_state.resume_text = ""
                st.session_state.roast_type = None
                st.rerun()
        with st.expander("📖 View Full Resume Content", expanded=False):
            st.text_area("Resume Content", st.session_state.resume_text, height=200, disabled=True)
        st.info(f"📊 Resume loaded: {len(st.session_state.resume_text)} characters, {len(st.session_state.resume_text.split())} words")
        st.markdown("---")
        st.markdown('<div class="brutality-section">', unsafe_allow_html=True)
        st.markdown("### 🔥 Choose Your Level of Brutality 💀")
        st.markdown("Select how you want your resume to be destroyed:")
        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                "💀 DEVASTATINGLY BRUTAL 💀",
                key="devastatingly_brutal",
                help="Prepare for complete annihilation. No mercy, no survivors.",
                use_container_width=True
            ):
                st.session_state.roast_type = "devastatingly_brutal"
                st.rerun()
        with col2:
            if st.button(
                "😭 SOUL CRUSHING 😭",
                key="soul_crushing", 
                help="Will make you cry and question everything. Emotional devastation guaranteed.",
                use_container_width=True
            ):
                st.session_state.roast_type = "soul_crushing"
                st.rerun()
        if st.session_state.roast_type == "devastatingly_brutal":
            st.success("💀 **DEVASTATINGLY BRUTAL SELECTED** 💀\n⚡ Prepare for complete annihilation ⚡\n🔥 No mercy, no survivors 🔥")
        elif st.session_state.roast_type == "soul_crushing":
            st.success("😭 **SOUL CRUSHING SELECTED** 😭\n💔 Will make you cry and question everything 💔\n🌪️ Emotional devastation guaranteed 🌪️")
        st.warning("⚠️ WARNING: This will be EXTREMELY brutal! This is for entertainment only. Don't take it seriously! ⚠️")
        st.markdown('</div>', unsafe_allow_html=True)
        if st.session_state.roast_type:
            st.markdown("---")
            if st.button("🔥 DESTROY MY RESUME NOW! ⚡💀", key="destroy_button", use_container_width=True):
                with st.spinner("🔥 Preparing your complete destruction... 💀"):
                    roast_result = generate_roast(client, st.session_state.resume_text, st.session_state.roast_type)
                    if roast_result:
                        st.markdown('<div class="roast-container">', unsafe_allow_html=True)
                        if st.session_state.roast_type == "devastatingly_brutal":
                            st.markdown("### 💀⚡ YOUR RESUME HAS BEEN DEVASTATINGLY DESTROYED ⚡💀")
                        else:
                            st.markdown("### 😭💔 YOUR RESUME HAS BEEN SOUL-CRUSHINGLY ANNIHILATED 💔😭")
                        st.markdown("---")
                        st.markdown(roast_result)
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.markdown("---")
                        if st.button("🔄 DESTROY ANOTHER RESUME", key="reset_btn", use_container_width=True):
                            st.session_state.roast_type = None
                            st.rerun()
                    else:
                        st.error("💥 Destruction failed! Try again.")
        else:
            st.info("👆 Select your preferred level of brutality above to proceed with the destruction!")
    else:
        st.info("👆 Upload your resume using one of the methods above to begin the destruction!")
    st.markdown("---")
    st.markdown("### 💀 DISCLAIMER ⚠️")
    st.markdown("This is purely for **ENTERTAINMENT PURPOSES** 🎭. The feedback is intentionally harsh and should not be taken seriously. Use this for fun, not as actual career advice! 😈")
    st.markdown("---")
    st.markdown("Made with 🔥💀 by **Resume Destroyer** | Powered by ⚡ **Groq AI** | *No resumes were harmed in the making of this app... just kidding, they were obliterated* 😂")

if __name__ == "__main__":
    main()
