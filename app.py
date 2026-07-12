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

# Initialisation du client officiel Google GenAI avec mise en cache
@st.cache_resource
def get_genai_client(api_key):
    return genai.Client(api_key=api_key)

client = get_genai_client(api_key)

# Prompt système officiel
SYSTEM_PROMPT = (
    "Tu es l'assistant virtuel officiel de la Banque Populaire. Tu es courtois, professionnel et précis. "
    "Tu aides les clients sur les offres de comptes, simulations de crédit et explication des documents. "
    "Reste toujours dans ton rôle de conseiller bancaire."
)

# Initialisation de la session de chat Gemini avec le modèle à jour (gemini-2.0-flash)
if "chat_session" not in st.session_state:
    st.session_state.chat_session = client.chats.create(
        model='gemini-2.0-flash',  # Modèle actuel recommandé et supporté par le SDK google-genai
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.3            # Température basse pour garantir la rigueur des réponses bancaires
        )
    )

# Initialisation de l'historique d'affichage Streamlit
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "model", "parts": ["Bonjour ! Comment puis-je vous aider aujourd'hui concernant vos services Banque Populaire ?"]}
    ]

# Affichage de l'historique de discussion
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["parts"][0])

# Zone de saisie utilisateur (Chat classique)
if user_input := st.chat_input("Posez votre question ici..."):
    st.session_state.messages.append({"role": "user", "parts": [user_input]})
    with st.chat_message("user"):
        st.write(user_input)
        
    with st.chat_message("model"):
        try:
            # Envoi du message dans la session de chat active
            response = st.session_state.chat_session.send_message(user_input)
            st.write(response.text)
            st.session_state.messages.append({"role": "model", "parts": [response.text]})
        except Exception as e:
            st.error(f"Détail de l'erreur : {str(e)}")

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
            text_content += page.extract_text() + "\n"
            
        if st.button("Analyser le document"):
            # Simulation visuelle dans le chat pour l'historique
            st.session_state.messages.append({"role": "user", "parts": ["[Document PDF envoyé pour analyse]"]})
            
            with st.chat_message("model"):
                st.info("Analyse du document en cours...")
                try:
                    # Transmission du contenu du document directement dans le fil de discussion
                    prompt_analyse = f"Voici un document bancaire téléchargé par le client. Analyse-le et fais-en un résumé clair et professionnel :\n\n{text_content}"
                    response = st.session_state.chat_session.send_message(prompt_analyse)
                    
                    # Mise à jour de l'historique de session et rafraîchissement de l'affichage
                    st.session_state.messages.append({"role": "model", "parts": [response.text]})
                    st.rerun() 
                except Exception as e:
                    st.error(f"Erreur lors de l'analyse : {str(e)}")
