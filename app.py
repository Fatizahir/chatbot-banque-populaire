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
