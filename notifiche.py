
import streamlit as st

st.title("Allarmi e Notifiche")
# Controlla lo stato dei lampioni e mostra gli avvisi
if st.session_state.gdf_lampioni is not None:
    # Filtra i lampioni non funzionanti
    guasti = st.session_state.gdf_lampioni[st.session_state.gdf_lampioni['Stato'] == 'Guasto']
    
    if not guasti.empty:
        with st.expander("Mostra Lampioni Non Funzionanti", expanded=False):
            for index, row in guasti.iterrows():
                st.error(f"Lampione {row['id']} non funziona! Intervento necessario.")
    else:
        st.success("Tutti i lampioni sono funzionanti.")