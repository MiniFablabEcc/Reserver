import streamlit as st
from utils.auth import process_login_request, is_authenticated
from utils.session import save_session_cookie

st.header("🔑 Connexion / Identité")

if is_authenticated():
    group_label = f"{st.session_state.group_type} {st.session_state.group_index}"
    st.success(f"Vous êtes déjà connecté en tant que {group_label}.")
    st.info("Vous pouvez aller à la page de réservation pour effectuer une réservation.")
    if st.button("Aller à la Réservation"):
        st.switch_page("app_pages/reservation.py")
elif st.session_state.get("is_bachelor", False):
    group_label = f"Bachelor {st.session_state.group_index}"
    st.success(f"Identité définie sur {group_label}.")
    st.info("Vous pouvez aller à la page de réservation pour effectuer une réservation.")
    if st.button("Aller à la Réservation"):
        st.switch_page("app_pages/reservation.py")
else:
    tab1, tab2 = st.tabs(["Groupes PLBD", "Groupes Bachelor"])
    
    with tab1:
        st.subheader("Connexion Étudiant PLBD")
        st.write("Entrez votre email de l'école pour recevoir un lien de connexion.")
        email = st.text_input("Email de l'école", placeholder="prenom.nom@centrale-casablanca.ma", key="plbd_email")
        
        if st.button("Envoyer le lien de connexion"):
            if email:
                base_url = st.secrets.get("general", {}).get("base_url", "http://localhost:8501")
                
                success, message = process_login_request(email, base_url)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.warning("Veuillez entrer une adresse email.")

    with tab2:
        st.subheader("Identité Étudiant Bachelor")
        st.write("Sélectionnez votre groupe et entrez votre email pour le suivi des réservations.")
        bachelor_group = st.selectbox("Sélectionner le Groupe", [1, 2, 3, 4], format_func=lambda x: f"Bachelor {x}")
        bachelor_email = st.text_input("Votre Email", placeholder="votre.email@example.com", key="bachelor_email")
        
        if st.button("Définir l'Identité"):
            if not bachelor_email:
                st.warning("Veuillez entrer votre adresse email.")
            else:
                st.session_state.logged_in = False
                st.session_state.is_bachelor = True
                st.session_state.group_type = "bachelor"
                st.session_state.group_index = bachelor_group
                st.session_state.user_email = bachelor_email
                # Save session to cookie for persistence
                save_session_cookie()
                st.success(f"Identité définie sur Bachelor {bachelor_group}. Vous pouvez maintenant faire des réservations.")
                st.rerun()

st.divider()
st.info("Remarque : Les groupes PLBD sont limités à 3 réservations en semaine et 5 le week-end. Les groupes Bachelor sont limités à 5 en semaine et 6 le week-end.")
