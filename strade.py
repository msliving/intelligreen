import streamlit as st
import pandas as pd
from shapely.geometry import Point


left, right = st.columns(2)
# Supponiamo di avere il tuo GeoDataFrame delle strade già caricato
gdf_strade = st.session_state.gdf_arcs

# Filtra le strade con affluenza "alta"
strade_trafficate = gdf_strade[gdf_strade['affluenza'] == 'alta']

# Conta il numero di strade trafficate per quartiere
strade_per_quartiere = strade_trafficate['nomequart'].value_counts().reset_index()
strade_per_quartiere.columns = ['Quartiere', 'Numero di Strade Trafficate']

with left:
    # Interfaccia Streamlit
    st.write("**Numero di Strade Trafficate per Quartiere**")
    st.dataframe(strade_per_quartiere, hide_index=True)



# Calcola la lunghezza totale delle strade per ciascun quartiere
lunghezza_per_quartiere = gdf_strade.groupby('nomequart')['lunghez'].sum().reset_index()
lunghezza_per_quartiere.columns = ['Quartiere', 'Lunghezza Totale Strade (mt)']

with right:
    # Interfaccia Streamlit
    st.write("**Lunghezza Totale delle Strade per Quartiere**")
    st.dataframe(lunghezza_per_quartiere, hide_index=True)

