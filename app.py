import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# Configuration de la page Streamlit
st.set_page_config(page_title="Assistant BP - Banque Populaire", page_icon="🏦", layout="centered")

# Style aux couleurs de la Banque Populaire (Orange et Bleu)
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

# Configuration de l'API Gemini via les Secrets de Streamlit
# On vérifie les deux noms possibles par sécurité
if "CLE_API_GEMINI" in st.secrets:
    genai.configure(api_key=st.secrets["CLE_API_GEMINI"])
elif "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Veuillez configurer votre clé API Gemini (GEMINI_API_KEY) dans les secrets de Streamlit.")
    st.stop()

# Initialisation du modèle de langage
model = genai.GenerativeModel('gemini-1.5-flash')

# Contexte (Prompt système) pour former l'IA en conseiller Banque Populaire
SYSTEM_PROMPT = """
Tu es l'assistant virtuel officiel de la Banque Populaire. Tu es courtois, professionnel et précis.
Tu aides les clients sur :
1. Les offres de comptes (Chaabi Net, cartes bancaires, comptes d'épargne).
2. Les simulations de crédit (Immobilier, Consommation).
3. L'explication des documents bancaires qu'ils téléchargent.
Reste toujours dans ton rôle de conseiller bancaire. Ne donne jamais de conseils financiers engageants sans suggérer de prendre RDV en agence.
"""

# Initialisation de l'historique des discussions
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "model", "parts": ["Bonjour ! Comment puis-je vous aider aujourd'hui concernant vos services Banque Populaire ?"]}
    ]

# Affichage de l'historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["parts"][0])

# Zone de saisie de l'utilisateur
if user_input := st.chat_input("Posez votre question ici..."):
    # Ajouter le message de l'utilisateur à l'historique
    st.session_state.messages.append({"role": "user", "parts": [user_input]})
    with st.chat_message("user"):
        st.write(user_input)
        
    # Appel à l'API Gemini
    with st.chat_message("model"):
        try:
            # On combine le prompt système avec l'historique pour donner du contexte
            full_prompt = f"{SYSTEM_PROMPT}\n\nHistorique :\n"
            for msg in st.session_state.messages[:-1]:
                full_prompt += f"{msg['role']}: {msg['parts'][0]}\n"
            full_prompt += f"User: {user_input}\nModel:"
            
            response = model.generate_content(full_prompt)
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
        # Extraction du texte du PDF
        reader = PdfReader(uploaded_file)
        text_content = ""
        for page in reader.pages:
            text_content += page.extract_text()
            
        if st.button("Analyser le document"):
            st.info("Analyse en cours...")
            # Simulation d'analyse avec le modèle
            analysis_prompt = f"{SYSTEM_PROMPT}\n\nAnalyse ce document bancaire et fais un résumé clair :\n{text_content}"
            try:
                response = model.generate_content(analysis_prompt)
                st.write(response.text)
            except Exception as e:
                st.error("Erreur lors de l'analyse du document.")
