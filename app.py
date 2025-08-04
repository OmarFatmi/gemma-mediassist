import gradio as gr
import json
import ollama
from modules.utils import load_json, call_gemma, load_prompt
from modules.stt import recognize_speech
from modules.tts import speak_text

# === Chargement des prompts ===
prompt_simplify    = load_prompt("simplify.txt")
prompt_translate_ar= load_prompt("translate_fr_ar.txt")
prompt_translate_en= load_prompt("translate_fr_en.txt")
prompt_profile     = load_prompt("profile_adapt.txt")
prompt_clarity     = load_prompt("clarity_eval.txt")
prompt_enrich      = load_prompt("enrich_term.txt")

# === Chargement des données ===
medical_terms    = load_json("data/medical_terms_fr_ar_en.json")
patient_profiles = load_json("data/patient_profiles.json")["profiles"]
recommendations  = load_json("data/recommendations.json")

# === Fonctions utilitaires ===
def search_in_dataset(term):
 term = term.lower()
 for entry in medical_terms:
     if term == entry["fr"].lower():
         return (
             f"🇫🇷 {entry['fr']}\n"
             f"🇸🇦 {entry['ar']}\n"
             f"🇬🇧 {entry['en']}\n\n"
             f"📄 {entry['definition']}"
         )
 return "Mot introuvable dans la base locale."

# === Modules métiers ===
def simplify_text(text):
 return call_gemma(prompt=prompt_simplify, input=text)

def translate_to_arabic(text):
 return call_gemma(prompt=prompt_translate_ar, input=text)

def translate_to_english(text):
 return call_gemma(prompt=prompt_translate_en, input=text)

def adapt_profile(text, profile_key):
 label = next((p['label'] for p in patient_profiles if p['key']==profile_key), profile_key)
 return call_gemma(prompt=prompt_profile, profile=label, input=text)

def get_recommendations(term):
 recs = recommendations.get(term.lower(), [])
 return "\n".join(f"- {r}" for r in recs) if recs else "Aucune recommandation disponible."

def enrich_with_gemma(term):
 response = call_gemma(prompt=prompt_enrich, input=term)
 # On attend "Traduction AR:…; Traduction EN:…; Définition:…;"
 parts = dict(part.split(":",1) for part in response.split(";") if ":" in part)
 ar = parts.get("Traduction AR", "").strip()
 en = parts.get("Traduction EN", "").strip()
 definition = parts.get("Définition", "").strip()
 medical_terms.append({"fr": term, "ar": ar, "en": en, "definition": definition})
 with open('data/medical_terms_fr_ar_en.json','w',encoding='utf-8') as f:
     json.dump(medical_terms, f, ensure_ascii=False, indent=2)
 return f"Terminé : {term} → AR: {ar}, EN: {en}\nDéfinition: {definition}"

def evaluate_clarity(text):
 return call_gemma(prompt=prompt_clarity, input=text)

def handle_chat(message, history):
    if history is None or not isinstance(history, list):
        history = []

    history.append({"role": "user", "content": message})

    response = ollama.chat(
        model="gemma:2b",
        messages=history
    )['message']['content']

    history.append({"role": "assistant", "content": response})

    return history, history


# === Interface Gradio unique ===
with gr.Blocks(title="Assistant Médical Local – Gemma 3n Multimodal") as demo:
 gr.Markdown("## 🩺 Assistant Médical Multimodal (offline)")

 # 🎙️ Parole & Audio
 with gr.Tab("🎙️ Parole & Audio"):
     stt_btn  = gr.Button("Enregistrer audio (5s)")
     stt_out  = gr.Textbox(label="Texte reconnu")
     stt_btn.click(fn=lambda: recognize_speech(5), inputs=None, outputs=stt_out)

     actions = ["Simplifier","FR→AR","FR→EN","Recommandations","Recherche locale"]
     proc_dropdown = gr.Dropdown(actions, label="Action audio")
     proc_btn      = gr.Button("Traiter")
     proc_out      = gr.Textbox(label="Résultat")

     def process_audio(text, action):
         if not text: return "Aucun texte reconnu."
         return {
             "Simplifier": simplify_text,
             "FR→AR": translate_to_arabic,
             "FR→EN": translate_to_english,
             "Recommandations": get_recommendations,
             "Recherche locale": search_in_dataset
         }.get(action, lambda x: "Action non reconnue.")(text)

     proc_btn.click(fn=process_audio, inputs=[stt_out, proc_dropdown], outputs=proc_out)
     gr.Button("Lire résultat").click(fn=speak_text, inputs=proc_out, outputs=None)

 # 📘 Simplification
 with gr.Tab("📘 Simplifier une phrase"):
     inp = gr.Textbox(label="Phrase médicale")
     out = gr.Textbox(label="Phrase simplifiée")
     gr.Button("Simplifier").click(fn=simplify_text, inputs=inp, outputs=out)

 # 🌍 Traduction FR→AR
 with gr.Tab("🌍 Traduire (FR → AR)"):
     inp = gr.Textbox(label="Texte en français")
     out = gr.Textbox(label="Traduction + explication en arabe")
     gr.Button("Traduire").click(fn=translate_to_arabic, inputs=inp, outputs=out)

 # 🌐 Traduction FR→EN
 with gr.Tab("🌐 Traduire (FR → EN)"):
     inp = gr.Textbox(label="Texte en français")
     out = gr.Textbox(label="Translation + explication simple en anglais")
     gr.Button("Translate").click(fn=translate_to_english, inputs=inp, outputs=out)

 # 👤 Adaptation Profil
 with gr.Tab("👤 Adapter au profil"):
     inp = gr.Textbox(label="Texte médical à adapter")
     selector = gr.Dropdown([p['label'] for p in patient_profiles], label="Profil")
     out = gr.Textbox(label="Texte adapté")
     gr.Button("Adapter").click(
         fn=lambda txt, lbl: adapt_profile(txt, next(p['key'] for p in patient_profiles if p['label']==lbl)),
         inputs=[inp, selector], outputs=out
     )

 # 💡 Recommandations santé
 with gr.Tab("💡 Recommandations santé"):
     inp = gr.Textbox(label="Mot médical (FR)")
     out = gr.Textbox(label="Recommandations")
     gr.Button("Obtenir").click(fn=get_recommendations, inputs=inp, outputs=out)

 # 🔎 Dictionnaire local
 with gr.Tab("🔎 Dictionnaire local"):
     inp = gr.Textbox(label="Mot (FR)")
     out = gr.Textbox(label="Résultat local")
     gr.Button("Rechercher").click(fn=search_in_dataset, inputs=inp, outputs=out)

 # ✍️ Enrichir dictionnaire
 with gr.Tab("✍️ Enrichir dictionnaire"):
     inp = gr.Textbox(label="Nouveau terme (FR)")
     out = gr.Textbox(label="Enrichissement")
     gr.Button("Générer & Ajouter").click(fn=enrich_with_gemma, inputs=inp, outputs=out)

 # ✅ Évaluation de clarté
 with gr.Tab("✅ Évaluation de clarté"):
     inp = gr.Textbox(label="Phrase simplifiée")
     out = gr.Textbox(label="Feedback de clarté")
     gr.Button("Évaluer").click(fn=evaluate_clarity, inputs=inp, outputs=out)

 # 🩺 Consultation simulée
 with gr.Tab("🩺 Consultation"):
    chatbot = gr.Chatbot(label="Consultation", type="messages")
    user_input = gr.Textbox(placeholder="Écrivez ici...", label="Votre message")
    chat_state = gr.State([])

    user_input.submit(fn=handle_chat, inputs=[user_input, chat_state], outputs=[chatbot, chat_state])


#  demo.launch()
demo.launch(share=True)
