                                            🩺 Gemma-MediAssist – Offline Medical Assistant

🔍 Overview

    Gemma-MediAssist is a multilingual, offline-ready AI assistant tailored for the healthcare sector. Designed for accessibility in rural or low-resource areas, this app provides text simplification, translation, medical advice, and spoken interaction — all without internet dependency.

🚀 Features

    🎙️ Speech-to-Text (STT) using Vosk (offline)

    🔊 Text-to-Speech (TTS) using pyttsx3

    📘 Medical Text Simplification

    🌍 Translation (French → Arabic / English)

    👤 Profile-Based Adaptation (e.g., for children or professionals)

    💡 Health Recommendations based on keyword input

    ➕ Dictionary Enrichment using LLM

    ✅ Clarity Evaluation

    💬 Chat Simulation powered by Ollama + Gemma 3n

🧱 Architecture


Frontend:     Gradio (Tabs + Blocks UI)
Backend:      Ollama (Gemma 3n via call_gemma wrapper)
Audio Modules:
   - STT: vosk
   - TTS: pyttsx3
Utils:        Prompt loading, JSON parsing, chat orchestration
Diagram:
(or provide your generated flowchart here)

📂 Folder Structure

        .
        ├── app.py
        ├── modules/
        │   ├── stt.py
        │   ├── tts.py
        │   └── utils.py
        ├── data/
        │   ├── medical_terms_fr_ar_en.json
        │   ├── recommendations.json
        │   └── patient_profiles.json
        ├── prompts/
        │   ├── simplify.txt
        │   ├── translate_fr_ar.txt
        │   ├── translate_fr_en.txt
        │   ├── profile_adapt.txt
        │   ├── clarity_eval.txt
        │   └── enrich_term.txt
        ├── models/
        │   └── vosk-model-small-fr/
        └── requirements.txt

🛠 Installation

    ✅ Prerequisites
    Python 3.10+

    Ollama

    Model: gemma:2b

🔧 Steps

    git clone https://github.com/your-user/gemma-mediassist.git
    cd gemma-mediassist

    # Create and activate virtual environment
    python -m venv venv
    .\venv\Scripts\activate         # Windows

    # Install dependencies
    pip install -r requirements.txt

    # Pull the Gemma model
    ollama pull gemma:2b

    # Run the app
    python app.py

🌐 Access (Optional)
    To share your app temporarily:

    demo.launch(share=True)
    This will generate a public URL you can share.

⚙️ Configuration Notes

    Modify modules/utils.py to customize the model name, prompt behavior, or chat strategy.

    Place your Vosk model in models/vosk-model-small-fr/

    Prompts are editable in prompts/

📌 Example Use Cases

    Simplify medical prescription text for elderly patients

    Translate French medical terms for Arabic-speaking users

    Simulate chatbot consultation with domain-specific advice

    Add and define new medical terms dynamically

    Use voice input to translate or simplify instantly

🧪 Testing

    Open the app in the browser (http://127.0.0.1:7860)

    Test each tab:

    Try STT with a 5s recording

    Use simplification on a complex sentence

    Translate "fièvre" to Arabic/English

    Switch profiles (child, adult) for adapted explanations

    Add your own term: "tachycardie"

📈 Future Improvements

    Fine-tuning Gemma with domain-specific corpus

    Add camera/video support for visual input

    Export explanations to PDF (for patients)

    Add multi-turn memory across chatbot interactions