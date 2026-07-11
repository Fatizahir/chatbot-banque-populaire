import streamlit as st
from google import genai
from google.genai import types
from pypdf import PdfReader

# Configuration de la page Streamlit
st.set_page_config(page_title="Assistant BP - Banque Populaire", page_icon="🏦", layout="centered")

# Style aux couleurs de la Banque Populaire
st.markdown("""
    <style>
    .main { background-color: #f5f7fa; }
    .stButton>button { background-color: #ff6600; color: white; border-radius: 8px; }
    .stTextInput>div>div>input { border-color: #003366; }
    h1 { color: #003366; }
    </style>
""", unsafe_allow_html=True)

st.title("🏦 Assistant Virtuel - Banque Populaire")
st.write("Bienvenue ! Je suis votre assistant IA. Je peux vous renseigner sur nos services ou analyser vos documents (Relevés, devis...).")

# Récupération de la clé API dans les Secrets
api_key = None
if "CLE_API_GEMINI" in st.secrets:
    api_key = st.secrets["CLE_API_GEMINI"]
elif "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]

if not api_key:
    st.error("Veuillez configurer votre clé API Gemini dans les secrets de Streamlit.")
    st.stop()

# Initialisation du client officiel Google GenAI
client = genai.Client(api_key=api_key)

# Prompt système
SYSTEM_PROMPT = """
Tu es l'assistant virtuel officiel de la Banque Populaire. Tu es courtois, professionnel et précis.
Tu aides les clients sur les offres de comptes, simulations de crédit et explication des documents.
Reste toujours dans ton rôle de conseiller bancaire.
"""

# Initialisation de l'historique
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "model", "parts": ["Bonjour ! Comment puis-je vous aider aujourd'hui concernant vos services Banque Populaire ?"]}
    ]

# Affichage de l'historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["parts"][0])

# Zone de saisie utilisateur
if user_input := st.chat_input("Posez votre question ici..."):
    st.session_state.messages.append({"role": "user", "parts": [user_input]})
    with st.chat_message("user"):
        st.write(user_input)
        
    with st.chat_message("model"):
        try:
            # Envoi simplifié pour le chat en 2026
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=user_input,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT
                )
            )
            st.write(response.text)
            st.session_state.messages.append({"role": "model", "parts": [response.text]})
        except Exception as e:
            st.error("Une erreur est survenue lors de la communication avec l'IA.")

# Barre latérale pour charger les fichiers PDF
with st.sidebar:
    st.header("📁 Analyse de Documents")
    st.write("Téléchargez un relevé de compte ou document (PDF)")
    uploaded_file = st.file_uploader("Upload", type=["pdf"])
    
    if uploaded_file is not None:
        st.success("Fichier chargé avec succès !")
        reader = PdfReader(uploaded_file)
        text_content = ""
        for page in reader.pages:
            text_content += page.extract_text()
            
        if st.button("Analyser le document"):
            st.info("Analyse en cours...")
            try:
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=f"Analyse ce document bancaire :\n{text_content}",
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT
                    )
                )
                st.write(response.text)
            except Exception as e:
                st.error("Erreur lors de l'analyse du document.")
