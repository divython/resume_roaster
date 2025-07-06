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

# --- THEME TOGGLE ---
def set_theme():
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark'
    theme = st.sidebar.radio('Theme', ['Dark', 'Light'], index=0 if st.session_state.theme=='dark' else 1)
    st.session_state.theme = theme.lower()
    return st.session_state.theme

def inject_theme_css(theme):
    if theme == 'dark':
        st.markdown('''<style>
            body, .stApp { background: #18181b !important; color: #e0e0e0 !important; }
            .stButton > button { background: #22223b; color: #fff; border-radius: 32px; font-weight: 900; border: none; padding: 1.1rem 2.5rem; margin: 0.5rem 0; font-size: 1.1rem; box-shadow: 0 2px 12px #2a003f44; transition: 0.2s; }
            .stButton > button.selected { background: linear-gradient(90deg, #ff1744 60%, #6a0572 100%) !important; color: #fff !important; box-shadow: 0 0 16px #ff1744cc, 0 0 32px #6a0572cc; }
            .stButton > button:hover { background: #3a3a5a; color: #fff; }
            .stTextArea textarea, .stFileUploader, .stTextInput input { background: #232336 !important; color: #e0e0e0 !important; border-radius: 16px !important; border: 1.5px solid #333 !important; }
            .stTextArea textarea:focus, .stTextInput input:focus { border: 2px solid #ff1744 !important; }
            .stAlert, .stInfo, .stSuccess, .stError, .stWarning { border-radius: 12px !important; }
            .stTabs [data-baseweb="tab"] { background: #232336 !important; color: #e0e0e0 !important; border-radius: 12px 12px 0 0 !important; }
            .stTabs [aria-selected="true"] { background: linear-gradient(90deg, #ff1744 60%, #6a0572 100%) !important; color: #fff !important; }
        </style>''', unsafe_allow_html=True)
    else:
        st.markdown('''<style>
            body, .stApp { background: #f7f7fa !important; color: #22223b !important; }
            .stButton > button { background: #e0e0e0; color: #22223b; border-radius: 32px; font-weight: 900; border: none; padding: 1.1rem 2.5rem; margin: 0.5rem 0; font-size: 1.1rem; box-shadow: 0 2px 12px #bbb4; transition: 0.2s; }
            .stButton > button.selected { background: linear-gradient(90deg, #ff1744 60%, #6a0572 100%) !important; color: #fff !important; box-shadow: 0 0 16px #ff1744cc, 0 0 32px #6a0572cc; }
            .stButton > button:hover { background: #6366f1; color: #fff; }
            .stTextArea textarea, .stFileUploader, .stTextInput input { background: #fff !important; color: #22223b !important; border-radius: 16px !important; border: 1.5px solid #bbb !important; }
            .stTextArea textarea:focus, .stTextInput input:focus { border: 2px solid #ff1744 !important; }
            .stAlert, .stInfo, .stSuccess, .stError, .stWarning { border-radius: 12px !important; }
            .stTabs [data-baseweb="tab"] { background: #e0e0e0 !important; color: #22223b !important; border-radius: 12px 12px 0 0 !important; }
            .stTabs [aria-selected="true"] { background: linear-gradient(90deg, #ff1744 60%, #6a0572 100%) !important; color: #fff !important; }
        </style>''', unsafe_allow_html=True)

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
    .main-header { font-family: 'Orbitron', sans-serif; font-size: 4.8rem; font-weight: 900; text-align: center; color: #e0e0e0; margin-bottom: 1rem; letter-spacing: 4px; text-transform: uppercase; text-shadow: 0 0 20px rgba(255, 23, 68, 0.8); }
    .subtitle { font-family: 'Inter', sans-serif; font-size: 1.8rem; text-align: center; color: #e0e0e0; margin-bottom: 3rem; font-weight: 300; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.7); }
    .processing-indicator { display: inline-flex; align-items: center; gap: 8px; font-family: 'Inter', sans-serif; font-weight: 500; margin-bottom: 1rem; }
    .speed-badge { padding: 6px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .speed-fast { background: linear-gradient(45deg, #4CAF50, #8BC34A); color: white; box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3); }
    .speed-normal { background: linear-gradient(45deg, #FF9800, #FFC107); color: white; box-shadow: 0 2px 8px rgba(255, 152, 0, 0.3); }
    .speed-slow { background: linear-gradient(45deg, #F44336, #E91E63); color: white; box-shadow: 0 2px 8px rgba(244, 67, 54, 0.3); }
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

def reddit_comment_box(text, username="u/ResumeDestroyer", upvotes=None, timeago="just now"):
    import random
    if upvotes is None:
        upvotes = random.randint(1, 9999)
    return f'''
    <div style="background:#232336;border-radius:12px;padding:1.2rem 1.5rem;margin:1.5rem 0;box-shadow:0 2px 16px #6a057244;">
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:0.5rem;">
        <span style="font-size:1.5rem;user-select:none;">⬆️</span>
        <span style="font-size:1.1rem;font-weight:700;color:#ff1744;">{upvotes}</span>
        <span style="font-size:1.5rem;user-select:none;">⬇️</span>
        <span style="margin-left:18px;font-size:1rem;color:#aaa;">{username} <span style='color:#888;font-size:0.95rem;'>· {timeago}</span></span>
      </div>
      <div style="font-size:1.13rem;line-height:1.7;font-family:'Inter',sans-serif;color:#e0e0e0;white-space:pre-wrap;">{text}</div>
    </div>
    '''

def main():
    theme = set_theme()
    inject_theme_css(theme)
    st.markdown('<div class="main-header" style="color:#ff1744;text-shadow:0 0 24px #6a0572;">🔥 Resume Destroyer</div>', unsafe_allow_html=True)
    st.caption('Upload your resume and prepare for total annihilation!')
    client = get_groq_client()
    st.divider()
    st.subheader('Upload Your Resume')
    tab1, tab2, tab3 = st.tabs(["Text Input", "PDF Upload", "Image Upload"])
    with tab1:
        text_input = st.text_area(
            "Paste your resume text here:",
            value=st.session_state.get('resume_text', ''),
            height=200,
            key="text_input_area"
        )
        if text_input != st.session_state.get('resume_text', ''):
            st.session_state.resume_text = text_input.strip()
    with tab2:
        pdf_file = st.file_uploader(
            "Upload PDF",
            type=['pdf'],
            key="pdf_uploader"
        )
        if pdf_file is not None:
            with st.spinner("Processing PDF..."):
                extracted_text = extract_text_from_pdf(pdf_file)
            if extracted_text:
                st.session_state.resume_text = extracted_text
                st.success("PDF processed!")
            else:
                st.error("Could not extract text from PDF.")
    with tab3:
        if not EASYOCR_AVAILABLE:
            st.info("Image processing not available. Please use Text or PDF upload.")
        image_file = st.file_uploader(
            "Upload Image",
            type=['png', 'jpg', 'jpeg'],
            key="image_uploader"
        )
        if image_file is not None and EASYOCR_AVAILABLE:
            st.image(image_file, caption="Your Resume", use_column_width=True)
            with st.spinner("Reading your resume with AI OCR..."):
                extracted_text = extract_text_from_image(image_file)
            if extracted_text:
                st.session_state.resume_text = extracted_text
                st.success("Image processed!")
            else:
                st.error("Could not extract text from image.")
    # --- Resume Preview ---
    resume_text = st.session_state.get('resume_text', '')
    if resume_text:
        st.divider()
        st.subheader('Resume Preview')
        st.text_area("Resume Content", resume_text, height=150, disabled=True, key="preview_area")
        st.info(f"Loaded: {len(resume_text)} characters, {len(resume_text.split())} words")
        st.divider()
        st.subheader('Choose Your Level of Brutality')
        selected = st.session_state.get('roast_type', None)
        c1, c2 = st.columns([1,1])
        with c1:
            if st.button("💀 Devastatingly Brutal", key="devastatingly_brutal_btn"):
                st.session_state.roast_type = "devastatingly_brutal"
        with c2:
            if st.button("😭 Soul Crushing", key="soul_crushing_btn"):
                st.session_state.roast_type = "soul_crushing"
        # Highlight selected by adding 'selected' class to the button
        st.markdown('''<script>
        let btns = window.parent.document.querySelectorAll('button[data-testid^="baseButton"]');
        btns.forEach(btn => { btn.classList.remove('selected'); });
        let selected = '%s';
        if(selected === 'devastatingly_brutal') btns[0].classList.add('selected');
        if(selected === 'soul_crushing') btns[1].classList.add('selected');
        </script>''' % (selected if selected else ''), unsafe_allow_html=True)
        # --- Destroy Button ---
        if selected:
            st.markdown('<div style="margin:32px 0 16px 0;text-align:center;">', unsafe_allow_html=True)
            destroy = st.button("🔥 DESTROY MY RESUME! ⚡💀", key="destroy_button", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            if destroy:
                with st.spinner("Preparing your destruction..."):
                    try:
                        roast_result = generate_roast(client, resume_text, selected)
                    except Exception as e:
                        st.error("😈 API call limit reached! Even the devil needs a break. Try again later or offer a sacrifice to the cloud gods.")
                        return
                if roast_result:
                    st.divider()
                    st.subheader('Reddit Roast Result')
                    st.markdown(reddit_comment_box(roast_result), unsafe_allow_html=True)
                    if st.button("Destroy Another Resume", key="reset_btn"):
                        st.session_state.resume_text = ''
                        st.session_state.roast_type = None
                        st.rerun()
                else:
                    st.error("Destruction failed! Try again.")
    else:
        st.info("Upload your resume using one of the methods above to begin.")
    st.divider()
    st.caption("This is for entertainment only. The feedback is intentionally harsh and should not be taken seriously.")
    st.caption("Made by Resume Destroyer | Powered by Groq AI")

if __name__ == "__main__":
    main()
