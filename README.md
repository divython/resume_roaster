# Resume Destroyer 🔥

A devilishly fun, AI-powered Streamlit app that roasts your resume with savage, Reddit-style comments. Upload your resume (text, PDF, or image), pick your brutality level, and prepare for total annihilation!

---

## Features
- **Dark/Light Theme Toggle**
- **Modern, minimal UI** with custom fonts and devilish color scheme
- **Two brutality levels**: Devastatingly Brutal 💀 or Soul Crushing 😭
- **Reddit-style roast output**: Multiple comments, nested replies, usernames, upvotes
- **Supports**: Text, PDF, and image (OCR) resume uploads
- **No data is saved**: All processing is in-memory; resumes are sent to Groq AI for roasting
- **Witty error handling** for API call limits
- **Fun disclaimers and warnings**

---

## Usage
1. **Clone this repo**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Set your Groq API key** as an environment variable or in Streamlit secrets:
   - Environment: `export GROQ_API_KEY=your_key`
   - Streamlit secrets: add to `.streamlit/secrets.toml`
4. **Run the app**:
   ```bash
   streamlit run streamlit_app.py
   ```
5. **Open in browser** and upload your resume for a roast!

---

## File Structure
- `streamlit_app.py` — Main Streamlit app (single file, all logic/UI)
- `requirements.txt` — Python dependencies

---

## Credits
- **Made by:** Divython
- **Powered by:** Groq AI, Gemini CLI, GitHub Copilot

---

## Disclaimer
> ⚠️ This app is for entertainment only! The feedback is intentionally harsh and should not be taken seriously. Your resume is not saved, but it is sent to Groq AI for processing. Use at your own risk!
