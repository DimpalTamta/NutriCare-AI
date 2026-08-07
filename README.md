# 🌿 NutriCare AI

### An Intelligent Multilingual AI-Powered Nutrition & Diet Assistant for Cancer Patients

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://nutricare-ai-dimpaltamta.streamlit.app)
[![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> **Supporting better nutrition, better recovery, better lives.**

---

## 📌 What is NutriCare AI?

NutriCare AI is an AI-powered nutrition assistant for cancer patients. It provides personalised, evidence-based dietary advice using **Retrieval-Augmented Generation (RAG)**.

- 💬 **Medical Chat** – Ask any nutrition question
- 🩺 **Symptom Assistant** – Get diet advice for specific symptoms
- 💉 **Treatment Assistant** – Diet plans for chemo, radiation, surgery
- 🍽 **Meal Planner** – Personalised daily meal plans
- 🥘 **Recipe Generator** – Generate recipes from ingredients
- 🥦 **Nutrient Lookup** – Nutrition facts for 2,110+ Indian foods
- 📊 **Food Comparison** – Compare two foods side-by-side
- 🌿 **Ayurvedic Remedies** – Traditional remedies with book search
- 📜 **Chat History** – All conversations saved

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/DimpalTamta/NutriCare-AI.git
cd NutriCare-AI
pip install -r requirements.txt
2. Create .env File
bash
GROQ_API_KEY=your_key_here
YOUTUBE_API_KEY=your_key_here
SPOONACULAR_API_KEY=your_key_here
GOOGLE_CUSTOM_SEARCH_API_KEY=your_key_here
GOOGLE_CUSTOM_SEARCH_ENGINE_ID=your_cx_id
3. Build FAISS Index
bash
python -c "from rag.load_documents import load_all_markdown; from rag.chunking import chunk_all_documents; from rag.vector_store import VectorStore; docs = load_all_markdown('knowledge_base/01_Medical_Knowledge'); chunks = chunk_all_documents(docs); store = VectorStore(); store.build_index(chunks); store.save(); print('✅ Done!')"
4. Run the App
bash
streamlit run app.py
🧠 How It Works
text
User Question
     ↓
FAISS Search (1406 chunks)
     ↓
Metadata Filtering (module-specific)
     ↓
Context Building
     ↓
Groq (Llama 3.3 70B)
     ↓
Evidence-based Answer
🗂️ Dataset
85 Medical Documents – Cancer nutrition, treatment, symptoms, nutrients

2,110+ Indian Foods – Nutrition database (CSV)

100+ Recipes – Indian recipes with nutrition (CSV)

Ayurvedic PDFs – User-uploaded for traditional remedies

🛠️ Tech Stack
Category	Technology
LLM	Groq (Llama 3.3 70B)
Embedding	all-MiniLM-L6-v2
Vector DB	FAISS
Framework	Streamlit
Image AI	CLIP (OpenAI)
TTS	gTTS
Translation	Google Translate
5 APIs Integrated
Groq – Main LLM

Google Translate – Multilingual support

YouTube Data – Recipe videos

Spoonacular – Extra nutrition data

Google Custom Search – Ayurvedic books

📸 Screenshots
Medical Chat	Symptom Assistant	Meal Planner
[Add Screenshot]	[Add Screenshot]	[Add Screenshot]
🌐 Live Demo
Try it here: https://nutricare-ai-dimpaltamta.streamlit.app

📁 Project Structure
text
NutriCare_AI/
├── app.py                 # Main app
├── rag/                   # RAG pipeline
├── llm/                   # LLM layer
├── memory/                # Conversation memory
├── voice/                 # Text-to-Speech
├── nutrition/             # Nutrition DB
├── recipe/                # Recipe DB
├── utils/                 # Utilities
├── knowledge_base/        # 85 MD files + CSVs
└── requirements.txt       # Dependencies
👨‍💻 Developer
Dimpal Tamta – MCA Student

GitHub: @DimpalTamta

Live App: NutriCare AI

🙏 Acknowledgements
National Cancer Institute (NCI)

American Cancer Society (ACS)

World Health Organization (WHO)

Mayo Clinic

ICMR & NIN (Indian food data)

⚠️ Disclaimer
This is for educational purposes only. Always consult your healthcare provider.
