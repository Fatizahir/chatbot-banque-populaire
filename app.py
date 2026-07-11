import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# Configuration de la page Streamlit
st.set_page_config(page_title="BP Assistant - Banque Populaire", page_icon="🏦", layout="centered")

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
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Veuillez configurer votre clé API Gemini (GEMINI_API_KEY) dans les secrets de Streamlit.")
    st.stop()

# Initialisation du modèle de langage
model = genai.GenerativeModel('gemini-1.5-flash')

# Contexte (Prompt système) pour formater l'IA en conseiller Banque Populaire
SYSTEM_PROMPT = """
Tu es l'assistant virtuel officiel de la Banque Populaire. Tu es courtois, professionnel et précis.
Tu aides les clients sur :
1. Les offres de comptes (Chaabi Net, cartes bancaires, comptes d'épargne).
2. Les simulations de crédit (Immobilier, Consommation).
3. L'explication des documents bancaires qu'ils téléchargent.
Reste toujours dans ton rôle de conseiller bancaire. Ne donne jamais de conseils financiers engageants sans suggérer de prendre RDV en agence.
"""

# Initialisation de l'historique de chat
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Bonjour ! Comment puis-je vous aider aujourd'hui concernant vos services Banque Populaire ?"}]

# --- ZONE DE TÉLÉCHARGEMENT DE DOCUMENT ---
st.sidebar.header("📂 Analyse de Documents")
uploaded_file = st.sidebar.file_uploader("Téléchargez un relevé de compte ou document (PDF)", type=["pdf"])

extracted_text = ""
if uploaded_file is not None:
    st.sidebar.success("Document chargé avec succès !")
    # Extraction du texte du PDF avec la bibliothèque 'pypdf'
    pdf_reader = PdfReader(uploaded_file)
    for page in pdf_reader.pages:
        extracted_text += page.extract_text()
    
    if st.sidebar.button("Analyser le document"):
        with st.spinner("Analyse du document en cours..."):
            prompt_analyse = f"En tant que conseiller Banque Populaire, analyse brièvement ce document et fais un résumé des points clés (montants, alertes ou opportunités pour le client) :\n\n{extracted_text}"
            try:
                response = model.generate_content(prompt_analyse)
                st.session_state.messages.append({"role": "assistant", "content": f"📝 **Analyse de votre document :**\n\n{response.text}"})
            except Exception as e:
                st.sidebar.error("Erreur lors de l'analyse du document.")

# --- INTERFACE DE CHAT ---

# Affichage des messages passés avec une clé unique pour stabiliser le rendu
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Entrée de l'utilisateur
if user_input := st.chat_input("Posez votre question ici..."):
    # Afficher et enregistrer le message de l'utilisateur
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Conteneur vide pour la réponse afin d'éviter le bug de rafraîchissement
    with st.chat_message("assistant"):
        placeholder = st.empty() # Crée un espace fixe dans l'interface
        with st.spinner("Recherche des informations..."):
            
            # Préparation du prompt complet
            full_prompt = f"{SYSTEM_PROMPT}\n\nHistorique de discussion:\n"
            for msg in st.session_state.messages[:-1]:
                full_prompt += f"{msg['role']}: {msg['content']}\n"
            full_prompt += f"User: {user_input}\nAssistant:"
            
            try:
                response = model.generate_content(full_prompt)
                reply = response.text
                
                # On écrit directement dans l'espace réservé
                placeholder.write(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                placeholder.error("Une erreur est survenue lors de la communication avec l'IA.")
