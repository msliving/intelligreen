import streamlit as st

st.set_page_config(layout="wide")

if "role" not in st.session_state:
    st.session_state.role = None

ROLES = ["Tecnico", "Admin"]

left, right = st.columns(2)
def login():
    
    with left:
        # Aggiungi spazi vuoti
        for _ in range(7):
            st.write(" ")  # Aggiungi righe vuot
        image_path = "images\img.png"  # Sostituisci con il percorso reale
        st.image(image_path, use_column_width=True)
    with right:
        for _ in range(7):
            st.write(" ")  # Aggiungi righe vuot
        st.header("Log in")
        role = st.selectbox("Choose your role", ROLES)
        if st.button("Log in"):
            st.session_state.role = role
            st.rerun()


def logout():
    st.session_state.role = None
    st.rerun()


role = st.session_state.role

logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
settings = st.Page("settings.py", title="Settings", icon=":material/settings:")

tecnico = st.Page("main.py", title="Tecnico", icon=":material/help:", default=(role == "Tecnico"),)
admin = st.Page("main.py", title="Admin", icon=":material/person:",default=(role == "Admin"),)

microgrid = st.Page("microgrid.py", title="Microgrid", icon=":material/bolt:")
lampioni = st.Page("lampioni.py", title="Lampioni", icon=":material/table_lamp:")
strade = st.Page("strade.py", title="Strade", icon=":material/road:")
notifiche = st.Page("notifiche.py", title="Notifiche", icon=":material/notifications_active:")

if st.session_state.role == "Tecnico":
    account_pages = [tecnico, settings, logout_page]
if st.session_state.role == "Admin":
    account_pages = [admin, settings, logout_page]

tecnico_pages = [notifiche]
admin_pages = [microgrid, lampioni, strade]

st.logo("images\logo.png")

page_dict = {}
if st.session_state.role in ["Tecnico", "Admin"]:
    page_dict["Segnalazioni"] = tecnico_pages
if st.session_state.role == "Admin":
    page_dict["Analisi"] = admin_pages

if len(page_dict) > 0:
    pg = st.navigation({"Account": account_pages} | page_dict)
else:
    pg = st.navigation([st.Page(login)])

pg.run()