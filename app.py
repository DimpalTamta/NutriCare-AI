# app.py – NutriCare AI v26 – No pygame, uses st.audio for TTS
import os, sys, time, pandas as pd, io, urllib.parse, re
from datetime import datetime
import streamlit as st
from PIL import Image
import altair as alt
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ---------- Imports ----------
from rag.load_documents import load_all_markdown
from rag.chunking import chunk_all_documents
from rag.vector_store import VectorStore
from rag.search import semantic_search, format_context, unique_sources
from rag.load_ayurvedic import load_ayurvedic_pdfs
from llm.prompt import build_rag_prompt, append_disclaimer, EXAMPLE_QUESTIONS
from llm.llm import generate_response
from nutrition.nutrition_db import get_nutrition, search_food
from recipe.recipe_db import search_recipes
from memory.memory import ConversationMemory
from utils.utils import ensure_dir, timestamp, get_logger
from utils.language_detector import LANGUAGE_CODES
from utils.api_helpers import search_youtube_video, get_spoonacular_nutrition, search_ayurvedic_books
from chat_db import init_db, save_chat, get_all_chats, clear_all_chats
from voice.voice import get_speech_bytes

# ---------- Translation ----------
try:
    from deep_translator import GoogleTranslator
    TRANS_AVAILABLE = True
except ImportError:
    TRANS_AVAILABLE = False
    GoogleTranslator = None

# ---------- PDF generation ----------
PDF_AVAILABLE = False
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    PDF_AVAILABLE = True
except ImportError:
    pass

# ---------- CLIP ----------
try:
    from transformers import CLIPProcessor, CLIPModel
    import torch
    CLIP_AVAILABLE = True
    clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
except ImportError:
    CLIP_AVAILABLE = False
    clip_model = None
    clip_processor = None

logger = get_logger("app")
init_db()

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="🌿 NutriCare AI", page_icon="🌿", layout="wide")

# -------------------- CSS (unchanged) --------------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #023020, #06402b, #0a5a3a, #0e6b44, #1a7d4a, #228B22, #2E8B57, #3A8F5A, #4C9A6A, #5A9A7A, #6AAA8A, #7ABAA0, #8ACAB0, #9ADAC0);
        background-size: 400% 400%;
        animation: gradientBG 20s ease infinite;
        color: #e8f5e9;
        font-family: 'Segoe UI', sans-serif;
    }
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    section[data-testid="stSidebar"] {
        background-color: #06402b !important;
        backdrop-filter: none !important;
        border-right: 1px solid #0a5a3a;
        color: #d0f0d0;
    }
    .stSidebar hr { border-top: 1px solid #4caf50 !important; opacity: 0.6; margin: 10px 0; }
    .stSidebar .stButton > button {
        background: linear-gradient(135deg, #f97316, #eab308, #22c55e) !important;
        background-size: 200% 200% !important;
        animation: gradientMove 4s ease infinite !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1rem !important;
        width: 100% !important;
        box-shadow: 0 4px 12px rgba(234, 179, 8, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    .stSidebar .stButton > button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(234, 179, 8, 0.6) !important;
    }
    .main-header {
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .main-header h1 {
        font-size: 2.8rem;
        font-weight: 700;
        color: #ffffff;
        text-shadow: 0 0 20px rgba(74, 222, 128, 0.3);
        margin: 0;
    }
    .main-header p {
        font-size: 1.2rem;
        color: #a5d6a7;
        font-style: italic;
        margin: 0;
        letter-spacing: 0.5px;
    }
    .answer-card {
        background-color: #ffffff;
        color: #1a1a1a;
        padding: 1.5rem 2rem;
        border-radius: 16px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        margin: 1rem 0;
        border-left: 6px solid #2e7d32;
        font-size: 1rem;
        line-height: 1.6;
        white-space: normal;
        overflow-wrap: break-word;
    }
    .answer-card h1, .answer-card h2, .answer-card h3, .answer-card h4 { color: #1a3a1a !important; }
    .answer-card strong { color: #2e7d32; }
    .answer-card ul, .answer-card ol { margin: 0.5rem 0; padding-left: 1.5rem; }
    .answer-card p { margin: 0.3rem 0; }
    .source-tag {
        display: inline-block;
        background-color: #e8f5e9;
        color: #1a5a2a;
        padding: 3px 12px;
        margin: 2px;
        border-radius: 12px;
        font-size: 0.75rem;
        border: 1px solid #2e7d32;
    }
    .chip-btn {
        background: transparent !important;
        border: 1px solid #4caf50 !important;
        color: white !important;
        border-radius: 24px !important;
        padding: 10px 20px !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        box-shadow: none !important;
        width: 100% !important;
        text-align: center !important;
        background-image: none !important;
        animation: none !important;
    }
    .chip-btn:hover {
        background: rgba(76, 175, 80, 0.15) !important;
        border-color: #66bb6a !important;
        transform: scale(1.02);
    }
    .stButton > button {
        background: linear-gradient(135deg, #f97316, #eab308, #22c55e) !important;
        background-size: 200% 200% !important;
        animation: gradientMove 4s ease infinite !important;
        color: white !important;
        border: none !important;
        border-radius: 30px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.8rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(234, 179, 8, 0.3) !important;
    }
    .stButton > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 8px 30px rgba(234, 179, 8, 0.6) !important;
    }
    .stButton > button:active { transform: scale(0.97) !important; }
    @keyframes gradientMove {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #1a2a1a !important;
        color: #e0f0e0 !important;
        border: 1px solid #2a5a2a !important;
        border-radius: 12px !important;
        box-shadow: none !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #4caf50 !important;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.2) !important;
    }
    .logo-container {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 0.2rem;
        font-size: 2.5rem;
        line-height: 1;
    }
    .logo-container span {
        background: linear-gradient(135deg, #4ade80, #16a34a);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 2rem;
    }
    .tagline { font-size: 1.0rem; color: #a5d6a7; margin-top: -0.2rem; font-style: italic; font-weight: 300; letter-spacing: 0.3px; }
    .sidebar-description { font-size: 0.95rem; line-height: 1.6; color: #c8e6c9; margin: 0.5rem 0; }
    .tech-item {
        background: rgba(255,255,255,0.06);
        padding: 4px 10px;
        border-radius: 6px;
        margin: 2px 0;
        font-size: 0.85rem;
        display: inline-block;
        border-left: 3px solid #4caf50;
    }
    .disclaimer {
        font-size: 0.8rem;
        color: #e0f0e0;
        text-align: center;
        padding-top: 1rem;
        border-top: 1px solid #2a5a2a;
    }
    .chat-thread {
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 8px;
        border-left: 3px solid #4caf50;
    }
    .chat-thread:hover {
        background: rgba(255,255,255,0.08);
    }
    .chat-question { font-weight: 600; color: #a5d6a7; cursor: pointer; }
    .chat-answer { color: #e0e0e0; font-size: 0.9rem; margin-top: 4px; }
    .chat-meta { font-size: 0.7rem; color: #90a8a8; }
    .about-card {
        background: rgba(255,255,255,0.05);
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 16px;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .about-card h3 { color: #4ade80; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

# -------------------- SESSION STATE --------------------
if "messages" not in st.session_state: st.session_state.messages = []
if "vector_store" not in st.session_state:
    st.session_state.vector_store = VectorStore()
    st.session_state.index_ready = st.session_state.vector_store.load()
if "memory" not in st.session_state: st.session_state.memory = ConversationMemory()
if "language" not in st.session_state: st.session_state.language = "English"
if "pending_question" not in st.session_state: st.session_state.pending_question = None
if "is_speaking" not in st.session_state: st.session_state.is_speaking = False
if "selected_chat" not in st.session_state: st.session_state.selected_chat = None
if "current_page" not in st.session_state: st.session_state.current_page = "Medical Chat"

# -------------------- HELPERS --------------------
def save_to_history(module, question, answer, sources=""):
    lang = st.session_state.language
    save_chat(module, question, answer, lang, sources)

def translate_text(text, dest_lang="hi"):
    if not TRANS_AVAILABLE or not text or dest_lang == "en":
        return text
    try:
        return GoogleTranslator(source='auto', target=dest_lang).translate(text)
    except Exception:
        return text

def clean_text(text):
    lines = text.split('\n')
    cleaned = []
    prev_empty = False
    for line in lines:
        is_empty = line.strip() == ''
        if not is_empty or not prev_empty:
            cleaned.append(line)
        prev_empty = is_empty
    return '\n'.join(cleaned)

def format_response(text):
    """Remove all heading symbols and convert to bold, remove Acknowledgement."""
    lines = text.split('\n')
    new_lines = []
    for line in lines:
        if re.match(r'^#+\s*Acknowledgement\s*', line.strip(), re.IGNORECASE):
            cleaned = re.sub(r'^#+\s*Acknowledgement\s*', '', line, flags=re.IGNORECASE)
            if cleaned.strip():
                new_lines.append(cleaned)
            continue
        if re.match(r'^#+\s*Key Information\s*$', line.strip(), re.IGNORECASE):
            new_lines.append('**Key Information**')
            continue
        if re.match(r'^#+\s*Practical Tips\s*$', line.strip(), re.IGNORECASE):
            new_lines.append('**Practical Tips**')
            continue
        if re.match(r'^\*\*Acknowledgement\*\*:?\s*$', line.strip(), re.IGNORECASE):
            continue
        cleaned = re.sub(r'^\s*\d+\.\s*\*\*?([^*]+)\*\*?:\s*', r'**\1:** ', line)
        if cleaned == line:
            cleaned = re.sub(r'^\s*\d+\.\s*([^:]+):\s*', r'**\1:** ', cleaned)
        new_lines.append(cleaned)
    result = '\n'.join(new_lines)
    return clean_text(result)

def create_multi_color_chart(data_dict, title="Nutrient Values"):
    if not data_dict:
        return None
    df = pd.DataFrame({"Nutrient": list(data_dict.keys()), "Value": list(data_dict.values())})
    color_scheme = alt.Scale(
        domain=df["Nutrient"].tolist(),
        range=['#f97316', '#eab308', '#22c55e', '#06b6d4', '#8b5cf6', '#ec4899', '#14b8a6']
    )
    chart = alt.Chart(df).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, opacity=0.85).encode(
        x=alt.X('Nutrient', sort=None, axis=alt.Axis(labelAngle=-20)),
        y=alt.Y('Value', axis=alt.Axis(gridColor='#2a5a2a')),
        color=alt.Color('Nutrient', scale=color_scheme, legend=None),
        tooltip=['Nutrient', 'Value']
    ).properties(title=title, width=600, height=350).configure_axis(
        labelColor='#c8e6c9', titleColor='#a5d6a7', gridColor='#2a5a2a'
    ).configure_title(color='#a5d6a7', fontSize=16)
    return chart

# ---------- TTS Functions (no pygame) ----------
def speak_text(text, lang="en"):
    if not text.strip():
        return
    try:
        audio_bytes = get_speech_bytes(text, lang=lang)
        if audio_bytes:
            st.session_state.audio_bytes = audio_bytes
            st.session_state.audio_text = text
            st.session_state.is_speaking = True
            st.rerun()
    except Exception as e:
        st.warning(f"TTS error: {e}")

def stop_speech():
    st.session_state.audio_bytes = None
    st.session_state.is_speaking = False
    st.rerun()

# ---------- PDF download ----------
def download_pdf(content, filename):
    if not PDF_AVAILABLE:
        st.download_button("📥 Download (as .txt)", data=content, file_name=filename.replace(".pdf", ".txt"), mime="text/plain")
        return
    try:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        y = height - 50
        c.setFont("Helvetica", 10)
        for line in content.split('\n'):
            if y < 50:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 10)
            if len(line) > 80:
                words = line.split()
                current = ""
                for w in words:
                    if len(current) + len(w) + 1 <= 80:
                        current += " " + w
                    else:
                        c.drawString(50, y, current.strip())
                        y -= 12
                        current = w
                if current:
                    c.drawString(50, y, current.strip())
                    y -= 12
            else:
                c.drawString(50, y, line)
                y -= 12
        c.save()
        pdf_bytes = buffer.getvalue()
        st.download_button("📥 Download PDF", data=pdf_bytes, file_name=filename, mime="application/pdf")
    except Exception:
        st.download_button("📥 Download (as .txt)", data=content, file_name=filename.replace(".pdf", ".txt"), mime="text/plain")

def format_nutrition_data(data):
    if not data:
        return {}
    mapping = {
        "food_name": "Food", "energy_kcal": "Energy (kcal)", "protein_g": "Protein (g)",
        "fat_g": "Fat (g)", "carb_g": "Carbohydrates (g)", "fibre_g": "Dietary Fiber (g)",
        "calcium_mg": "Calcium (mg)", "iron_mg": "Iron (mg)", "magnesium_mg": "Magnesium (mg)",
        "potassium_mg": "Potassium (mg)", "sodium_mg": "Sodium (mg)", "zinc_mg": "Zinc (mg)",
        "vita_ug": "Vitamin A (µg)", "vite_mg": "Vitamin E (mg)", "vitc_mg": "Vitamin C (mg)",
        "folate_ug": "Folate (µg)", "vitb1_mg": "Vitamin B1 (mg)", "vitb2_mg": "Vitamin B2 (mg)",
        "vitb3_mg": "Vitamin B3 (mg)", "vitb6_mg": "Vitamin B6 (mg)", "phosphorus_mg": "Phosphorus (mg)",
        "selenium_ug": "Selenium (µg)", "copper_mg": "Copper (mg)", "manganese_mg": "Manganese (mg)",
        "cholesterol_mg": "Cholesterol (mg)", "sfa_mg": "Saturated Fat (mg)",
        "mufa_mg": "Monounsaturated Fat (mg)", "pufa_mg": "Polyunsaturated Fat (mg)",
    }
    formatted = {}
    for key, display in mapping.items():
        if key in data:
            val = data[key]
            if val is not None and val != "":
                formatted[display] = val
    return formatted

def recognize_food_from_image(image_bytes):
    if not CLIP_AVAILABLE:
        return None
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        df = pd.read_csv("knowledge_base/02_Nutrition_Database/indian_food_database.csv", encoding='latin-1')
        food_names = df["food_name"].dropna().unique().tolist()[:100]
        inputs = clip_processor(text=food_names, images=image, return_tensors="pt", padding=True)
        with torch.no_grad():
            outputs = clip_model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)
        best_idx = probs.argmax().item()
        best_food = food_names[best_idx]
        confidence = probs[0][best_idx].item()
        if confidence > 0.05:
            return best_food, confidence
        return None
    except Exception:
        return None

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.markdown("""
    <div class="logo-container">
        <span>🌿</span>
        <span>NutriCare AI</span>
    </div>
    <div class="tagline">Supporting better nutrition, better recovery, better lives.</div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    pages = ["Medical Chat", "Symptom", "Treatment", "Meal Planner", "Recipe", "Nutrient", "Compare", "Ayurvedic Remedies", "Chat History", "About Us"]
    for p in pages:
        if st.button(p, key=f"nav_{p}", use_container_width=True):
            st.session_state.current_page = p
            st.rerun()
    st.markdown("---")
    st.session_state.language = st.selectbox("🌐 Language", ["English", "Hindi", "Marathi"])
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        clear_all_chats()
        st.session_state.messages = []
        st.session_state.memory.clear()
        st.session_state.selected_chat = None
        st.rerun()
    st.markdown("---")
    st.markdown("### ⚙️ Tech Stack & APIs")
    st.markdown("""
    <div style="display: flex; flex-wrap: wrap; gap: 4px;">
        <span class="tech-item">🔹 LLM: Groq (Llama 3.3 70B)</span><br>
        <span class="tech-item">🔹 Embedding: all-MiniLM-L6-v2</span><br>
        <span class="tech-item">🔹 Vector DB: FAISS</span><br>
        <span class="tech-item">🔹 Framework: Streamlit</span><br>
        <span class="tech-item">🔹 Image AI: CLIP</span><br>
        <span class="tech-item">🔹 Translation: Google Translate</span><br>
        <span class="tech-item">🔹 TTS: gTTS (via st.audio)</span><br>
        <span class="tech-item">🔹 PDF: ReportLab</span><br>
        <span class="tech-item">🔹 APIs: Groq, Google Translate, YouTube Data, Spoonacular, Google Custom Search</span><br>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Powered by Groq · FAISS · CLIP · Streamlit")

# -------------------- MAIN AREA --------------------
st.markdown("""
<div class="main-header">
    <h1>🌿 NutriCare AI</h1>
    <p>Supporting better nutrition, better recovery, better lives.</p>
</div>
""", unsafe_allow_html=True)

page = st.session_state.current_page

# ==================== Medical Chat ====================
if page == "Medical Chat":
    st.markdown("#### Try asking:")
    cols = st.columns(3)
    for i, q in enumerate(EXAMPLE_QUESTIONS[:6]):
        with cols[i % 3]:
            if st.button(q, key=f"chip_{i}"):
                st.session_state.pending_question = q
                st.rerun()

    for turn in st.session_state.messages:
        if turn["role"] == "user":
            with st.chat_message("user"):
                st.markdown(turn["content"])
        else:
            formatted = format_response(turn["content"])
            st.markdown(f'<div class="answer-card">{formatted}</div>', unsafe_allow_html=True)
            if turn.get("sources"):
                tags = " ".join(f'<span class="source-tag">{s}</span>' for s in turn["sources"])
                st.markdown(tags, unsafe_allow_html=True)

    user_input = st.chat_input("Ask about nutrition, symptoms, or recipes...")
    if st.session_state.pending_question and not user_input:
        user_input = st.session_state.pending_question
        st.session_state.pending_question = None

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                store = st.session_state.vector_store
                if not store.is_ready:
                    answer = "Knowledge base not ready. Please check the vector store."
                    sources = []
                else:
                    results = semantic_search(user_input, store, top_k=5)
                    context = format_context(results)
                    history = st.session_state.memory.format_history()
                    prompt = build_rag_prompt(user_input, context, history)
                    raw = generate_response(prompt)
                    raw = raw.replace("Acknowledgement:", "").strip()
                    answer = append_disclaimer(raw)
                    sources = unique_sources(results)
                    lang_code = LANGUAGE_CODES.get(st.session_state.language, "en")
                    if lang_code != "en":
                        answer = translate_text(answer, lang_code)
                formatted_answer = format_response(answer)
                st.markdown(f'<div class="answer-card">{formatted_answer}</div>', unsafe_allow_html=True)
                if sources:
                    tags = " ".join(f'<span class="source-tag">{s}</span>' for s in sources)
                    st.markdown(tags, unsafe_allow_html=True)

                col_sp1, col_sp2 = st.columns(2)
                with col_sp1:
                    if st.button("🔊 Speak", key="speak_medical"):
                        speak_text(answer, lang_code)
                        if st.session_state.get("audio_bytes"):
                            st.audio(st.session_state.audio_bytes, format="audio/mp3")
                with col_sp2:
                    if st.button("⏹ Stop", key="stop_medical"):
                        stop_speech()

        st.session_state.memory.add_turn(user_input, answer)
        st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
        save_to_history("Medical Chat", user_input, answer, ", ".join(sources))
        st.rerun()

# ==================== Symptom ====================
elif page == "Symptom":
    st.markdown("### Symptom-Based Diet Advice")
    symptom = st.text_input("Enter your symptom (e.g., nausea, mouth sores)")
    lang_code = LANGUAGE_CODES.get(st.session_state.language, "en")
    if st.button("Get Advice", key="symptom_get") and symptom:
        with st.spinner("Searching..."):
            results = semantic_search(f"Diet for {symptom}", st.session_state.vector_store, top_k=5)
            context = format_context(results)
            prompt = f"""You are a compassionate oncology dietitian. Give specific foods to eat, foods to avoid, and hydration tips for the symptom: {symptom}.
            Use only the context.
            Context: {context}
            Answer:"""
            raw = generate_response(prompt)
            raw = raw.replace("Acknowledgement:", "").strip()
            answer = append_disclaimer(raw)
            if lang_code != "en":
                answer = translate_text(answer, lang_code)
            sources = unique_sources(results)
            st.session_state._symptom_answer = answer
            st.session_state._symptom_sources = sources
            st.session_state._symptom_query = symptom
            st.rerun()
    if "_symptom_answer" in st.session_state:
        formatted = format_response(st.session_state._symptom_answer)
        st.markdown(f'<div class="answer-card">{formatted}</div>', unsafe_allow_html=True)
        if st.session_state._symptom_sources:
            tags = " ".join(f'<span class="source-tag">{s}</span>' for s in st.session_state._symptom_sources)
            st.markdown(tags, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔊 Speak Symptom", key="speak_symptom"):
                speak_text(st.session_state._symptom_answer, lang_code)
                if st.session_state.get("audio_bytes"):
                    st.audio(st.session_state.audio_bytes, format="audio/mp3")
        with col2:
            if st.button("⏹ Stop", key="stop_symptom"):
                stop_speech()
        save_to_history("Symptom", f"Symptom: {st.session_state._symptom_query}", st.session_state._symptom_answer, ", ".join(st.session_state._symptom_sources))

# ==================== Treatment ====================
elif page == "Treatment":
    st.markdown("### Treatment-Based Nutrition")
    treatment = st.selectbox("Select Treatment", ["Chemotherapy", "Radiation", "Surgery", "Immunotherapy", "Hormone Therapy"])
    lang_code = LANGUAGE_CODES.get(st.session_state.language, "en")
    if st.button("Get Diet Plan", key="treatment_get") and treatment:
        with st.spinner("Generating..."):
            results = semantic_search(f"Nutrition for {treatment}", st.session_state.vector_store, top_k=5)
            context = format_context(results)
            prompt = f"""You are an oncology nutritionist. Provide pre‑treatment, during‑treatment, and post‑treatment dietary advice for {treatment}.
            Context: {context}
            Answer:"""
            raw = generate_response(prompt)
            raw = raw.replace("Acknowledgement:", "").strip()
            answer = append_disclaimer(raw)
            if lang_code != "en":
                answer = translate_text(answer, lang_code)
            sources = unique_sources(results)
            st.session_state._treatment_answer = answer
            st.session_state._treatment_sources = sources
            st.session_state._treatment_query = treatment
            st.rerun()
    if "_treatment_answer" in st.session_state:
        formatted = format_response(st.session_state._treatment_answer)
        st.markdown(f'<div class="answer-card">{formatted}</div>', unsafe_allow_html=True)
        if st.session_state._treatment_sources:
            tags = " ".join(f'<span class="source-tag">{s}</span>' for s in st.session_state._treatment_sources)
            st.markdown(tags, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔊 Speak Treatment", key="speak_treatment"):
                speak_text(st.session_state._treatment_answer, lang_code)
                if st.session_state.get("audio_bytes"):
                    st.audio(st.session_state.audio_bytes, format="audio/mp3")
        with col2:
            if st.button("⏹ Stop", key="stop_treatment"):
                stop_speech()
        save_to_history("Treatment", f"Treatment: {st.session_state._treatment_query}", st.session_state._treatment_answer, ", ".join(st.session_state._treatment_sources))

# ==================== Meal Planner ====================
elif page == "Meal Planner":
    st.markdown("### Personalized Meal Planner")
    with st.form("meal_plan"):
        age = st.number_input("Age", min_value=1, max_value=120, value=50)
        gender = st.selectbox("Gender", ["Male", "Female"])
        diet = st.radio("Diet", ["Vegetarian", "Non-Vegetarian"])
        treatment = st.selectbox("Current Treatment", ["None", "Chemotherapy", "Radiation", "Surgery"])
        symptoms = st.text_input("Any symptoms? (optional)")
        cuisine = st.selectbox("Cuisine", ["Indian", "Chinese", "Italian", "Other"])
        meals = st.selectbox("Meals per day", [3,4,5])
        submitted = st.form_submit_button("Generate Plan")
    if submitted:
        query = f"Create a meal plan for a {age}-year-old {gender}, {diet}, undergoing {treatment}, symptoms: {symptoms}, cuisine: {cuisine}, {meals} meals/day."
        with st.spinner("Planning..."):
            results = semantic_search(query, st.session_state.vector_store, top_k=5)
            context = format_context(results)
            prompt = f"You are a dietitian. Generate a daily meal plan with breakfast, lunch, dinner, snacks, hydration, calories, and safety tips.\nContext: {context}\nQuestion: {query}\nAnswer:"
            raw = generate_response(prompt)
            raw = raw.replace("Acknowledgement:", "").strip()
            answer = append_disclaimer(raw)
            lang_code = LANGUAGE_CODES.get(st.session_state.language, "en")
            if lang_code != "en":
                answer = translate_text(answer, lang_code)
            sources = unique_sources(results)
            st.session_state._meal_answer = answer
            st.session_state._meal_sources = sources
            st.session_state._meal_query = query
    if "_meal_answer" in st.session_state:
        formatted = format_response(st.session_state._meal_answer)
        st.markdown(f'<div class="answer-card">{formatted}</div>', unsafe_allow_html=True)
        if st.session_state._meal_sources:
            tags = " ".join(f'<span class="source-tag">{s}</span>' for s in st.session_state._meal_sources)
            st.markdown(tags, unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔊 Speak Meal Plan", key="speak_meal"):
                speak_text(st.session_state._meal_answer, lang_code)
                if st.session_state.get("audio_bytes"):
                    st.audio(st.session_state.audio_bytes, format="audio/mp3")
        with col2:
            if st.button("⏹ Stop", key="stop_meal"):
                stop_speech()
        with col3:
            download_pdf(st.session_state._meal_answer, f"meal_plan_{timestamp()}.pdf")
        save_to_history("Meal Planner", st.session_state._meal_query, st.session_state._meal_answer, ", ".join(st.session_state._meal_sources))

# ==================== Recipe ====================
elif page == "Recipe":
    st.markdown("### AI Recipe Generator")
    ingredients = st.text_area("Enter ingredients (comma separated)", "Rice, Paneer, Tomato, Capsicum")
    lang_code = LANGUAGE_CODES.get(st.session_state.language, "en")
    if st.button("Generate Recipe", key="recipe_gen"):
        with st.spinner("Creating..."):
            recipes = search_recipes(ingredients, limit=3)
            if recipes:
                rec = recipes[0]
                answer = f"### {rec.get('recipe_name', 'Recipe')}\n\n"
                answer += f"**Cuisine:** {rec.get('cuisine', '')}  |  **Time:** {rec.get('total_time', '')}\n\n"
                answer += f"**Calories:** {rec.get('calories', '')} kcal  |  **Protein:** {rec.get('protein', '')}g\n\n"
                answer += f"**Ingredients:** {rec.get('ingredients', '')}\n\n"
                answer += f"**Instructions:** {rec.get('instructions', '')}\n\n"
                if lang_code != "en":
                    answer = translate_text(answer, lang_code)
                st.session_state._recipe_answer = answer
                st.session_state._recipe_sources = "Recipe DB"
                st.session_state._recipe_name = rec.get('recipe_name', 'Recipe')
            else:
                results = semantic_search(f"Recipe with {ingredients}", st.session_state.vector_store, top_k=5)
                context = format_context(results)
                prompt = f"Create a recipe using {ingredients}. Provide name, time, steps, nutrition, alternatives, and cancer-friendly notes.\nContext: {context}\nAnswer:"
                raw = generate_response(prompt)
                raw = raw.replace("Acknowledgement:", "").strip()
                answer = append_disclaimer(raw)
                if lang_code != "en":
                    answer = translate_text(answer, lang_code)
                st.session_state._recipe_answer = answer
                st.session_state._recipe_sources = ", ".join(unique_sources(results))
                match = re.search(r'###\s*(Recipe[:\s]*.*?)\n', answer)
                st.session_state._recipe_name = match.group(1).strip() if match else "Recipe"
    if "_recipe_answer" in st.session_state:
        formatted = format_response(st.session_state._recipe_answer)
        st.markdown(f'<div class="answer-card">{formatted}</div>', unsafe_allow_html=True)
        if st.session_state._recipe_sources and st.session_state._recipe_sources != "Recipe DB":
            tags = " ".join(f'<span class="source-tag">{s}</span>' for s in st.session_state._recipe_sources.split(", "))
            st.markdown(tags, unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("🔊 Speak Recipe", key="speak_recipe"):
                speak_text(st.session_state._recipe_answer, lang_code)
                if st.session_state.get("audio_bytes"):
                    st.audio(st.session_state.audio_bytes, format="audio/mp3")
        with col2:
            if st.button("⏹ Stop", key="stop_recipe"):
                stop_speech()
        with col3:
            download_pdf(st.session_state._recipe_answer, f"recipe_{timestamp()}.pdf")
        with col4:
            if st.button("🎬 Watch Video"):
                video_ids = search_youtube_video(st.session_state._recipe_name)
                if video_ids:
                    embed_url = f"https://www.youtube.com/embed/{video_ids[0]}"
                    st.markdown(f'<iframe width="560" height="315" src="{embed_url}" frameborder="0" allowfullscreen></iframe>', unsafe_allow_html=True)
                    if len(video_ids) > 1:
                        st.write("More videos:")
                        for vid in video_ids[1:]:
                            st.markdown(f'- [Watch on YouTube](https://www.youtube.com/watch?v={vid})')
                else:
                    query = urllib.parse.quote_plus(st.session_state._recipe_name + " recipe")
                    youtube_url = f"https://www.youtube.com/results?search_query={query}"
                    st.markdown(f'<a href="{youtube_url}" target="_blank"><button style="background-color:#2e7d32; color:white; border:none; border-radius:30px; padding:0.4rem 1.6rem; font-weight:500; cursor:pointer;">🎬 YouTube Search</button></a>', unsafe_allow_html=True)
        save_to_history("Recipe", f"Ingredients: {ingredients}", st.session_state._recipe_answer, st.session_state._recipe_sources)

# ==================== Nutrient ====================
elif page == "Nutrient":
    st.markdown("### Indian Food Nutrition Lookup")
    nutrient_method = st.radio("Search by:", ["Text", "Image"], horizontal=True)

    if nutrient_method == "Text":
        food = st.text_input("Enter food name (e.g., Paneer, Rice)")
        if st.button("Lookup", key="nutrient_text") and food:
            matches = search_food(food, limit=5)
            if not matches:
                st.warning("Food not found.")
            else:
                selected = st.selectbox("Did you mean:", matches)
                data = get_nutrition(selected)
                if data:
                    clean_data = format_nutrition_data(data)
                    if clean_data:
                        df_clean = pd.DataFrame([clean_data]).T
                        df_clean.columns = ["Value"]
                        st.dataframe(df_clean)
                        macro_keys = ["Energy (kcal)", "Protein (g)", "Fat (g)", "Carbohydrates (g)", "Dietary Fiber (g)"]
                        macro_vals = {k: clean_data.get(k, 0) for k in macro_keys if k in clean_data}
                        if macro_vals:
                            chart = create_multi_color_chart(macro_vals, f"Nutrients in {selected}")
                            if chart:
                                st.altair_chart(chart, use_container_width=True)
                        if st.button("🔍 Get Extra Nutrition from Spoonacular", key="spoonacular_btn"):
                            with st.spinner("Fetching from Spoonacular..."):
                                spoon_data = get_spoonacular_nutrition(selected)
                                if spoon_data:
                                    st.subheader("Spoonacular Data")
                                    st.write(f"**Food:** {spoon_data.get('name', '')}")
                                    st.write(f"**Calories:** {spoon_data.get('calories', 'N/A')} kcal")
                                    st.write(f"**Protein:** {spoon_data.get('protein', 'N/A')} g")
                                    st.write(f"**Fat:** {spoon_data.get('fat', 'N/A')} g")
                                    st.write(f"**Carbs:** {spoon_data.get('carbs', 'N/A')} g")
                                else:
                                    st.info("Spoonacular API not available or no extra data.")
                    else:
                        st.warning("No nutrient data available for this food.")
                else:
                    st.warning("No data found.")
                save_to_history("Nutrient Lookup", f"Food: {food}", f"Nutrients for {selected}", "Nutrition DB")

    else:
        uploaded_file = st.file_uploader("Upload a food image (JPG, PNG)", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            image_bytes = uploaded_file.read()
            st.image(image_bytes, caption="Uploaded Image", width=250)
            if st.button("🔍 Identify Food & Show Nutrition", key="nutrient_image"):
                if CLIP_AVAILABLE:
                    with st.spinner("Identifying food using AI..."):
                        result = recognize_food_from_image(image_bytes)
                    if result:
                        food_name, confidence = result
                        st.success(f"Identified as: **{food_name}** (confidence: {confidence:.2f})")
                        data = get_nutrition(food_name)
                        if data:
                            clean_data = format_nutrition_data(data)
                            if clean_data:
                                df_clean = pd.DataFrame([clean_data]).T
                                df_clean.columns = ["Value"]
                                st.dataframe(df_clean)
                                macro_keys = ["Energy (kcal)", "Protein (g)", "Fat (g)", "Carbohydrates (g)", "Dietary Fiber (g)"]
                                macro_vals = {k: clean_data.get(k, 0) for k in macro_keys if k in clean_data}
                                if macro_vals:
                                    chart = create_multi_color_chart(macro_vals, f"Nutrients in {food_name}")
                                    if chart:
                                        st.altair_chart(chart, use_container_width=True)
                            else:
                                st.warning("No nutrient data available for this food.")
                        else:
                            st.warning("Food not found in the nutrition database.")
                        save_to_history("Nutrient Lookup (Image)", f"Image: {uploaded_file.name}", f"Identified as {food_name}", "AI + Nutrition DB")
                    else:
                        st.error("Could not identify the food. Please try a clearer image or use text search.")
                else:
                    st.warning("Image recognition not available (CLIP not installed). Please use text search.")

# ==================== Compare ====================
elif page == "Compare":
    st.markdown("### Compare Two Foods")
    food1 = st.text_input("Food 1", "Paneer")
    food2 = st.text_input("Food 2", "Tofu")
    if st.button("Compare", key="compare") and food1 and food2:
        d1 = get_nutrition(food1)
        d2 = get_nutrition(food2)
        if d1 and d2:
            f1 = format_nutrition_data(d1)
            f2 = format_nutrition_data(d2)
            if f1 and f2:
                common_keys = set(f1.keys()) & set(f2.keys())
                if common_keys:
                    comp_data = {}
                    for k in sorted(common_keys):
                        comp_data[k] = [f1.get(k, "N/A"), f2.get(k, "N/A")]
                    df_comp = pd.DataFrame(comp_data, index=[food1, food2]).T
                    st.dataframe(df_comp)
                    st.write("**Comparison Summary**")
                    metrics = ["Energy (kcal)", "Protein (g)", "Fat (g)", "Carbohydrates (g)", "Dietary Fiber (g)"]
                    for m in metrics:
                        if m in f1 and m in f2:
                            v1 = f1[m]
                            v2 = f2[m]
                            try:
                                v1_f = float(v1)
                                v2_f = float(v2)
                                if v1_f > v2_f:
                                    better = food1
                                elif v2_f > v1_f:
                                    better = food2
                                else:
                                    better = "both are equal"
                                st.write(f"- **{m}**: {v1} vs {v2} → {better} is higher")
                            except:
                                st.write(f"- **{m}**: {v1} vs {v2}")
                else:
                    st.warning("No common nutrients to compare.")
            else:
                st.warning("One or both foods have no nutrient data.")
        else:
            st.warning("One or both foods not found.")
        save_to_history("Food Comparison", f"Compare {food1} and {food2}", f"Comparison: {food1} vs {food2}", "Nutrition DB")

# ==================== Ayurvedic Remedies ====================
elif page == "Ayurvedic Remedies":
    st.markdown("### 🌿 Ayurvedic & Home Remedies")
    
    with st.expander("📤 Upload Ayurvedic PDF (optional)"):
        uploaded_pdf = st.file_uploader("Upload a PDF (Ayurvedic book, home remedies, nuskha)", type=["pdf"])
        if uploaded_pdf is not None:
            ensure_dir("knowledge_base/04_Ayurvedic_Knowledge")
            path = os.path.join("knowledge_base/04_Ayurvedic_Knowledge", uploaded_pdf.name)
            with open(path, "wb") as f:
                f.write(uploaded_pdf.getbuffer())
            st.success(f"Uploaded {uploaded_pdf.name}")
            with st.spinner("Rebuilding knowledge base..."):
                md_docs = load_all_markdown("knowledge_base/01_Medical_Knowledge")
                ayu_docs = load_ayurvedic_pdfs("knowledge_base/04_Ayurvedic_Knowledge")
                all_docs = md_docs + ayu_docs
                chunks = chunk_all_documents(all_docs)
                store = VectorStore()
                store.build_index(chunks)
                store.save()
                st.session_state.vector_store = store
                st.session_state.index_ready = True
            st.success("Knowledge base updated with Ayurvedic content!")
            st.rerun()

    st.markdown("---")
    st.write("**Ask about home remedies or traditional treatments:**")
    remedy_question = st.text_input("e.g., 'Home remedy for nausea', 'Ayurvedic treatment for mouth sores'")
    lang_code = LANGUAGE_CODES.get(st.session_state.language, "en")
    if st.button("Get Remedy", key="remedy_get") and remedy_question:
        with st.spinner("Searching..."):
            store = st.session_state.vector_store
            if store.is_ready:
                results = semantic_search(remedy_question, store, top_k=5)
                context = format_context(results)
            else:
                context = ""
                results = []
            prompt = f"""You are a traditional medicine expert. Provide Ayurvedic or home remedies for: {remedy_question}.
            Use the context (which includes Ayurvedic texts if available). If the remedy is from Ayurvedic sources, clearly mention it.
            If no context is available, use your general knowledge about Ayurvedic remedies.
            Context: {context}
            Answer:"""
            raw = generate_response(prompt)
            raw = raw.replace("Acknowledgement:", "").strip()
            answer = append_disclaimer(raw)
            if lang_code != "en":
                answer = translate_text(answer, lang_code)
            sources = unique_sources(results)
            st.markdown(f'<div class="answer-card">{format_response(answer)}</div>', unsafe_allow_html=True)
            if sources:
                tags = " ".join(f'<span class="source-tag">{s}</span>' for s in sources)
                st.markdown(tags, unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔊 Speak Remedy", key="speak_remedy"):
                    speak_text(answer, lang_code)
                    if st.session_state.get("audio_bytes"):
                        st.audio(st.session_state.audio_bytes, format="audio/mp3")
            with col2:
                if st.button("⏹ Stop", key="stop_remedy"):
                    stop_speech()
            save_to_history("Ayurvedic Remedies", remedy_question, answer, ", ".join(sources))

    st.markdown("---")
    st.subheader("📚 Search Ayurvedic Books Online")
    book_query = st.text_input("Search term (e.g., 'nausea home remedy')")
    if st.button("Search Books", key="book_search") and book_query:
        with st.spinner("Searching..."):
            results = search_ayurvedic_books(book_query)
            if results:
                st.success(f"Found {len(results)} results")
                for item in results:
                    st.markdown(f"**{item['title']}**")
                    st.write(item['snippet'])
                    st.markdown(f"[Read more]({item['link']})")
                    st.markdown("---")
            else:
                st.warning("No results found. Check API key or try a different query.")

# ==================== Chat History ====================
elif page == "Chat History":
    st.markdown("### 📜 Chat History")
    st.caption("Click on any question to view the full answer.")
    
    if st.session_state.selected_chat:
        chat = st.session_state.selected_chat
        st.markdown(f"""
        <div class="chat-thread" style="border-left-color: #f97316;">
            <div style="font-weight:600; color:#4ade80;">📌 {chat['question']}</div>
            <div style="margin-top:8px; background:#1a2a1a; padding:12px; border-radius:8px; color:#e0e0e0;">
                {chat['answer']}
            </div>
            <div class="chat-meta" style="margin-top:8px;">
                🕐 {chat['timestamp']} · 📂 {chat['module']} · 🌐 {chat['language']}
                {f' · 📄 {chat["sources"]}' if chat.get("sources") else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("← Back to History List"):
            st.session_state.selected_chat = None
            st.rerun()
        st.markdown("---")
    
    chats = get_all_chats(limit=100)
    if chats:
        for chat in chats:
            if st.button(f"💬 {chat['question'][:60]}...", key=f"chat_{chat['timestamp']}", use_container_width=True):
                st.session_state.selected_chat = chat
                st.rerun()
        st.markdown("---")
        if st.button("Export All as CSV"):
            df = pd.DataFrame(chats)
            csv = df.to_csv(index=False)
            st.download_button("Download CSV", data=csv, file_name="chat_history.csv", mime="text/csv")
    else:
        st.info("No chat history yet.")

# ==================== About Us ====================
elif page == "About Us":
    st.markdown("""
    <div style="text-align:center; margin-bottom:24px;">
        <h2 style="color:#a5d6a7;">🌿 About NutriCare AI</h2>
        <p style="font-size:1.1rem; color:#c8d8d8;">An Intelligent Multilingual AI-Powered Nutrition & Diet Assistant for Cancer Patients</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="about-card">
            <h3>👨‍💻 Developer</h3>
            <p><strong>Name:</strong> Dimpal Tamta<br>
            <strong>Course:</strong> MCA<br>
            <strong>Project:</strong> Major Project – LLM & RAG</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="about-card">
            <h3>🎯 Project Goal</h3>
            <p>To provide <strong>personalised, evidence‑based, and compassionate</strong> nutrition guidance for cancer patients, caregivers, and dietitians, with support for <strong>traditional Ayurvedic remedies</strong>.</p>
            <p>Built using <strong>Retrieval-Augmented Generation (RAG)</strong> with a custom knowledge base of 85 medical documents, 2110+ Indian foods, and 100+ recipes.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="about-card">
            <h3>📚 APIs Used</h3>
            <ul style="color:#c8d8d8; padding-left:20px;">
                <li><strong>1.</strong> Groq (Llama 3.3 70B) – Main LLM</li>
                <li><strong>2.</strong> Google Translate – Multilingual (English, Hindi, Marathi)</li>
                <li><strong>3.</strong> YouTube Data API – Recipe video search</li>
                <li><strong>4.</strong> Spoonacular API – Extra nutrition data</li>
                <li><strong>5.</strong> Google Custom Search – Ayurvedic book search</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="about-card">
            <h3>🧠 Technology Stack</h3>
            <ul style="color:#c8d8d8; padding-left:20px;">
                <li><strong>LLM:</strong> Groq (Llama 3.3 70B)</li>
                <li><strong>Embedding:</strong> all-MiniLM-L6-v2</li>
                <li><strong>Vector DB:</strong> FAISS</li>
                <li><strong>Framework:</strong> Streamlit</li>
                <li><strong>Image AI:</strong> CLIP (OpenAI)</li>
                <li><strong>Translation:</strong> Google Translate API</li>
                <li><strong>TTS:</strong> gTTS (via st.audio)</li>
                <li><strong>PDF:</strong> ReportLab</li>
                <li><strong>Data:</strong> Pandas, NumPy</li>
                <li><strong>Visualization:</strong> Altair</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="about-card">
            <h3>🔗 Links</h3>
            <ul style="color:#c8d8d8; padding-left:20px;">
                <li><strong>GitHub:</strong> <a href="#" style="color:#4ade80;">Link to repository</a></li>
                <li><strong>Deployment:</strong> <a href="#" style="color:#4ade80;">Streamlit Cloud link</a></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="about-card" style="border-left: 4px solid #f97316;">
        <h3>⚠️ Disclaimer</h3>
        <p style="color:#c8d8d8; margin:0;">This is for <strong>educational purposes only</strong>. Always consult your healthcare provider.</p>
        <p style="color:#90a8a8; margin-top:4px; font-style:italic;">Made with ❤️ for cancer patients and their families.</p>
    </div>
    """, unsafe_allow_html=True)

# -------------------- FOOTER --------------------
st.markdown("---")
st.markdown('<p class="disclaimer">NutriCare AI provides general educational information only and is not a substitute for professional medical advice.</p>', unsafe_allow_html=True)
