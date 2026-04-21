import streamlit as st
from utils.auth import check_auth_token, is_authenticated
from utils.admin import is_admin
from utils.session import load_session_from_cookie, clear_session_cookie

st.set_page_config(
    page_title="Réservation MiniFabLab",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "group_type" not in st.session_state:
    st.session_state.group_type = None
if "group_index" not in st.session_state:
    st.session_state.group_index = None

# Check for token in URL (login via link)
check_auth_token()

# Restore session from cookie if not already logged in
if not st.session_state.get("group_type"):
    load_session_from_cookie()

# Define navigation
pages = []
pages.append(st.Page("app_pages/login.py", title="Connexion / Identité", icon=":material/login:"))
pages.append(st.Page("app_pages/reservation.py", title="Faire une Réservation", icon=":material/event:"))
pages.append(st.Page("app_pages/dashboard.py", title="Planning Actuel", icon=":material/dashboard:"))

if is_authenticated() and is_admin(st.session_state.user_email):
    pages.append(st.Page("app_pages/admin.py", title="Panneau d'Admin", icon=":material/admin_panel_settings:"))

pg = st.navigation(pages)

# Sidebar info
with st.sidebar:
    st.title("MiniFabLab")
    if is_authenticated():
        group_label = f"{st.session_state.group_type} {st.session_state.group_index}"
        st.success(f"Connecté en tant que : {group_label}")
        st.write(f"Email : {st.session_state.user_email}")
        if st.button("Se déconnecter"):
            clear_session_cookie()
            st.session_state.logged_in = False
            st.session_state.user_email = None
            st.session_state.group_type = None
            st.session_state.group_index = None
            st.session_state.is_bachelor = False
            st.rerun()
    elif st.session_state.get("is_bachelor", False):
        group_label = f"Bachelor {st.session_state.group_index}"
        st.info(f"Identité : {group_label}")
        if st.button("Réinitialiser l'Identité"):
            clear_session_cookie()
            st.session_state.is_bachelor = False
            st.session_state.group_type = None
            st.session_state.group_index = None
            st.session_state.user_email = None
            st.rerun()
    else:
        st.warning("Non connecté (PLBD) ou Identité non définie (Bachelor)")

pg.run()
