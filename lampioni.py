import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import plotly.express as px
import matplotlib.pyplot as plt

col1, col2, col3 = st.columns([1.5, 2, 1.5])

# Supponiamo di avere i tuoi GeoDataFrame già caricati
quartieri = st.session_state.gdf_quartieri
zone = st.session_state.gdf_zone
aree = st.session_state.gdf_aree
lampioni = st.session_state.gdf_lampioni
gdf_strade = st.session_state.gdf_arcs  # GeoDataFrame delle strade


# Funzione per contare lampioni in ogni quartiere
def count_lampioni_in_quartieri(quartieri, lampioni):
    lampioni_count = {quartiere['quartiere']: 0 for _, quartiere in quartieri.iterrows()}
    for _, lampione in lampioni.iterrows():
        point = Point(lampione.geometry.x, lampione.geometry.y)
        for _, quartiere in quartieri.iterrows():
            if quartiere.geometry.contains(point):
                lampioni_count[quartiere['quartiere']] += 1
                break
    return lampioni_count

# Conteggio lampioni per quartiere
lampioni_count_quartieri = count_lampioni_in_quartieri(quartieri, lampioni)
df_quartieri = pd.DataFrame(list(lampioni_count_quartieri.items()), columns=['Quartiere', 'Lampioni'])

# Funzione per contare i lampioni in ogni zona
def count_lampioni_in_zone(zones, lampioni):
    zone_count = {zone['zona_fiu']: 0 for _, zone in zones.iterrows()}
    for _, lampione in lampioni.iterrows():
        point = Point(lampione.geometry.x, lampione.geometry.y)
        for _, zona in zones.iterrows():
            if zona.geometry.contains(point):
                zone_count[zona['zona_fiu']] += 1
                break
    return zone_count

# Conteggio lampioni per zona
lampioni_count_zone = count_lampioni_in_zone(zone, lampioni)
df_zone = pd.DataFrame(list(lampioni_count_zone.items()), columns=['Zona', 'Lampioni'])

# Funzione per contare i lampioni in ogni area
def count_lampioni_in_area(aree, lampioni):
    area_count = {area['area_statistica']: 0 for _, area in aree.iterrows()}
    for _, lampione in lampioni.iterrows():
        point = Point(lampione.geometry.x, lampione.geometry.y)
        for _, area in aree.iterrows():
            if area.geometry.contains(point):
                area_count[area['area_statistica']] += 1
                break
    return area_count

# Conteggio lampioni per area
lampioni_count_area = count_lampioni_in_area(aree, lampioni)
df_area = pd.DataFrame(list(lampioni_count_area.items()), columns=['Area', 'Lampioni'])

# Unire i dati in un DataFrame per il grafico
df_plot = pd.DataFrame({
    'Tipo': ['Quartiere'] * len(df_quartieri) + ['Zona'] * len(df_zone) + ['Area'] * len(df_area),
    'Nome': list(df_quartieri['Quartiere']) + list(df_zone['Zona']) + list(df_area['Area']),
    'Lampioni': list(df_quartieri['Lampioni']) + list(df_zone['Lampioni']) + list(df_area['Lampioni']),
})

# Creazione del grafico a linee orizzontali con Plotly
fig = px.bar(
    df_plot,
    x='Lampioni',
    y='Nome',
    color='Tipo',
    orientation='h',
    title='Numero di Lampioni per Quartiere, Zona e Area',
    labels={'Nome': 'Nome', 'Lampioni': 'Numero di Lampioni'},
    text='Lampioni'
)

# Aggiornare il layout per migliorare l'aspetto e aumentare l'altezza
fig.update_layout(
    yaxis_title='Nome',
    xaxis_title='Numero di Lampioni',
    barmode='group',
    height=800  # Imposta l'altezza a 800 pixel (puoi modificarlo come preferisci)
)

with col1:
    # Interfaccia Streamlit per visualizzare le tabelle
    st.write('**Numero di Lampioni per Quartiere**')
    st.dataframe(df_quartieri, hide_index=True)

with col2:
    st.write('**Numero di Lampioni per Zona**')
    st.dataframe(df_zone, hide_index=True)

with col3:
    st.write('**Numero di Lampioni per Area**')
    st.dataframe(df_area, hide_index=True)

# Mostrare il grafico in Streamlit
st.plotly_chart(fig)

##################
col21, col22, col23 = st.columns([1.5, 1.5, 1.5])

def count_lampioni_per_tipo(lampioni):
    return lampioni.groupby('Tipo').size()

# Conteggio lampioni per tipo
lampioni_count_tipo = count_lampioni_per_tipo(lampioni)
df_tipo = pd.DataFrame(lampioni_count_tipo).reset_index()
df_tipo.columns = ['Tipo', 'Lampioni']

# Interfaccia Streamlit per visualizzare la tabella dei lampioni per tipo
with col21:
    st.write('**Numero di Lampioni per Tipo**')
    st.dataframe(df_tipo, hide_index=True)


# Funzione per contare lampioni per tecnologia
def count_lampioni_per_tecnologia(lampioni):
    return lampioni.groupby('Tecnologia').size()

# Conteggio lampioni per tecnologia
lampioni_count_tecnologia = count_lampioni_per_tecnologia(lampioni)
df_tecnologia = pd.DataFrame(lampioni_count_tecnologia).reset_index()
df_tecnologia.columns = ['Tecnologia', 'Lampioni']

with col22:
    # Interfaccia Streamlit per visualizzare la tabella dei lampioni per tecnologia
    st.write('**Numero di Lampioni per Tecnologia**')
    st.dataframe(df_tecnologia, hide_index=True)


#########àà


# Grafico a torta
# Grafico a torta
if lampioni is not None:
    stato_counts = lampioni['Stato'].value_counts()
    
    # Crea un grafico a torta con uno stile migliorato
    fig, ax = plt.subplots(figsize=(6, 4))  # Imposta una dimensione più piccola del grafico (6x4 pollici)
    
    # Aggiungi il grafico a torta
    wedges, texts, autotexts = ax.pie(
        stato_counts,
        labels=stato_counts.index,
        autopct='%1.1f%%',
        startangle=90,
        colors=['#4CAF50', '#F44336'],  # Colori personalizzati: verde e rosso
        explode=(0.1, 0),  # Esplodi il primo wedge (funzionanti)
        shadow=True,  # Aggiungi ombra
    )

    # Personalizza i testi delle percentuali
    for text in autotexts:
        text.set_color('white')  # Colore bianco per il testo percentuale
        text.set_fontsize(10)  # Dimensione del carattere più piccola
    
    # Imposta l'aspetto del grafico
    plt.setp(texts, size=10, weight="bold")  # Dimensione e peso dei testi
    with col23:
        # Mostra il grafico
        st.write("**Percentuale di Lampioni per Stato**")
        st.pyplot(fig)

# Supponiamo di avere il tuo DataFrame lampioni già caricato
st.subheader("Info Lampioni")

# Rinominare le colonne del DataFrame, ad esempio:
lampioni.rename(columns={
    'quartiere_ID': 'Quartiere',  # Modifica il nome della colonna Stato

    # Aggiungi altre colonne se necessario
}, inplace=True)

# Se desideri riordinare le colonne, specifica l'ordine desiderato
# Per esempio, se vuoi solo alcune colonne in un certo ordine
lampioni = lampioni[['id','Tipo','Tecnologia','Intensità luminosa','Energia consumata', 'Stato', 'Quartiere']]  # Aggiungi altre colonne se necessario


# Visualizza il DataFrame
st.dataframe(lampioni, hide_index=True)
