import streamlit as st
import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import streamlit as st


# Supponiamo di avere i tuoi GeoDataFrame già caricati
gdf_quartieri = st.session_state.gdf_quartieri
gdf_zone = st.session_state.gdf_zone
gdf_aree = st.session_state.gdf_aree
gdf_lamp = st.session_state.gdf_lampioni
gdf_strade = st.session_state.gdf_arcs # GeoDataFrame delle strade

# Verifica se i GeoDataFrame sono vuoti
if gdf_quartieri.empty or gdf_zone.empty or gdf_aree.empty or gdf_lamp.empty or gdf_strade.empty:
    st.warning("Uno o più GeoDataFrame sono vuoti. Controlla i dati.")
else:
    # Conta i quartieri per microgrid
    quartieri_per_microgrid = gdf_quartieri.groupby('microgrid').agg(
        Numero_Quartieri=('quartiere', 'size'),
        Nomi_Quartieri=('quartiere', lambda x: ', '.join(x))
    ).reset_index()

    # Aggiungi la colonna 'quartiere' nei GeoDataFrame
    gdf_zone['quartiere'] = gdf_zone['nomequart']
    gdf_lamp['quartiere'] = gdf_lamp['quartiere_ID']  # Controlla il nome della colonna
    gdf_aree['quartiere'] = gdf_aree['quartiere']
    gdf_strade['quartiere'] = gdf_strade['nomequart']  # Collega le strade al nome del quartiere

    # Unisci i GeoDataFrame delle zone, lampioni e strade ai quartieri
    zone_con_quartiere = gdf_zone.merge(
        gdf_quartieri[['quartiere', 'microgrid']],
        on='quartiere',
        how='left'
    )

    lamp_con_quartiere = gdf_lamp.merge(
        gdf_quartieri[['quartiere', 'microgrid']],
        on='quartiere',
        how='left'
    )

    strade_con_quartiere = gdf_strade.merge(
        gdf_quartieri[['quartiere', 'microgrid']],
        left_on='quartiere',
        right_on='quartiere',
        how='left'
    )

    # Conta le zone per microgrid
    zone_per_microgrid = zone_con_quartiere.groupby('microgrid').size().reset_index(name='Numero Zone')

    # Conta i lampioni per microgrid
    lamp_per_microgrid = lamp_con_quartiere.groupby('microgrid').size().reset_index(name='Numero Lampioni')

    # Conta i lampioni guasti e funzionanti per microgrid
    lampioni_guasti = lamp_con_quartiere[lamp_con_quartiere['Stato'] == 'Guasto'].groupby('microgrid').size().reset_index(name='Numero Lampioni Guasti')
    lampioni_funzionanti = lamp_con_quartiere[lamp_con_quartiere['Stato'] == 'Funzionante'].groupby('microgrid').size().reset_index(name='Numero Lampioni Funzionanti')

    # Conta le aree per microgrid
    aree_con_quartiere = gdf_aree.merge(
        gdf_quartieri[['quartiere', 'microgrid']],
        on='quartiere',
        how='left'
    )
    aree_per_microgrid = aree_con_quartiere.groupby('microgrid').size().reset_index(name='Numero Aree')

    # Conta le strade per microgrid
    strade_per_microgrid = strade_con_quartiere.groupby('microgrid').size().reset_index(name='Numero Strade')

    # Conta le strade affollate per microgrid
    strade_affollate = strade_con_quartiere[strade_con_quartiere['affluenza'] == 'alta'].groupby('microgrid').size().reset_index(name='Numero Strade Affollate')

    # Unisci i risultati
    microgrid_summary = quartieri_per_microgrid \
        .merge(zone_per_microgrid, on='microgrid', how='left') \
        .merge(aree_per_microgrid, on='microgrid', how='left') \
        .merge(lamp_per_microgrid, on='microgrid', how='left') \
        .merge(lampioni_guasti, on='microgrid', how='left') \
        .merge(lampioni_funzionanti, on='microgrid', how='left') \
        .merge(strade_per_microgrid, on='microgrid', how='left') \
        .merge(strade_affollate, on='microgrid', how='left')

    # Sostituisci i NaN con 0 se ci sono microgrid senza zone, aree, lampioni o strade
    microgrid_summary.fillna(0, inplace=True)

    # Rinomina le colonne per rimuovere gli underscore
    microgrid_summary.columns = ['Microgrid', 'Quartieri', 'Nomi Quartieri', 'Zone', 'Aree', 'Lampioni', 'Lampioni Guasti', 'Lampioni Funzionanti', 'Strade', 'Strade Affollate']

    # Mostra il risultato nella tua app Streamlit
    st.dataframe(microgrid_summary, hide_index=True)



# Calcola efficienza media per microgrid
#L'efficienza media che stiamo calcolando rappresenta l'efficienza media energetica dei lampioni per ciascuna microgrid, basata sul rapporto tra l'intensità luminosa e l'energia consumata dai lampioni funzionanti all'interno di quella microgrid.
#In altre parole, questa metrica ci dà un'indicazione di quanto efficientemente ogni microgrid utilizza l'energia per l'illuminazione stradale
    
left, right = st.columns(2)
import matplotlib.pyplot as plt
import streamlit as st

# Supponiamo di avere i tuoi GeoDataFrame già caricati
gdf_quartieri = st.session_state.gdf_quartieri
gdf_lamp = st.session_state.gdf_lampioni

# Verifica se i GeoDataFrame sono vuoti
if gdf_quartieri.empty or gdf_lamp.empty:
    st.warning("Uno o più GeoDataFrame sono vuoti. Controlla i dati.")
else:
    with left:
        # Unisci i lampioni ai quartieri per ottenere la microgrid di ciascun lampione
        lamp_con_quartiere = gdf_lamp.merge(
            gdf_quartieri[['quartiere', 'microgrid']],
            on='quartiere',
            how='left'
        )

        # Calcola l’efficienza per ogni lampione: Intensità luminosa / Energia consumata, se funzionante
        lamp_con_quartiere['Efficienza'] = lamp_con_quartiere.apply(
            lambda row: row['Intensità luminosa'] / row['Energia consumata']
            if row['Energia consumata'] > 0 and row['Stato'] == 'Funzionante' else 0,
            axis=1
        )

        # Calcola l’efficienza media per ciascuna microgrid
        efficienza_per_microgrid = lamp_con_quartiere.groupby('microgrid')['Efficienza'].mean().reset_index(name='Efficienza Media (lm/W)')

        # Visualizza la tabella dell'efficienza media per microgrid
        st.write("**Efficienza Media per Microgrid**")
        st.write("Indicazione di quanto efficientemente ogni microgrid utilizza l'energia per l'illuminazione stradale. Rapporto tra l'intensità luminosa e l'energia consumata dai lampioni funzionanti all'interno di quella microgrid.")
        st.dataframe(efficienza_per_microgrid, hide_index=True)

    with right:
        #
        # Crea un grafico a torta dell'efficienza media per microgrid
        fig, ax = plt.subplots(figsize=(8, 6))  # Imposta le dimensioni della figura

        ax.pie(efficienza_per_microgrid['Efficienza Media (lm/W)'], labels=efficienza_per_microgrid['microgrid'], autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie chart is a circle.

        ax.set_title("Distribuzione dell'Efficienza Media per Microgrid")

        # Mostra il grafico nella tua app Streamlit
        st.pyplot(fig)




# Supponiamo di avere i tuoi GeoDataFrame già caricati
gdf_quartieri = st.session_state.gdf_quartieri
gdf_lamp = st.session_state.gdf_lampioni

# Verifica se i GeoDataFrame sono vuoti
if gdf_quartieri.empty or gdf_lamp.empty:
    st.warning("Uno o più GeoDataFrame sono vuoti. Controlla i dati.")
else:
    # Unisci i lampioni ai quartieri per ottenere la microgrid di ciascun lampione
    lamp_con_quartiere = gdf_lamp.merge(
        gdf_quartieri[['quartiere', 'microgrid']],
        on='quartiere',
        how='left'
    )

    # Calcola l’energia consumata per ciascun lampione
    # Assumiamo che l'energia consumata sia già presente nel gdf_lamp, puoi modificarlo se necessario
    # Nota: Assicurati che il campo "Energia consumata" esista e abbia un nome corretto
    # Calcola l'energia totale per ciascuna microgrid
    energia_per_microgrid = lamp_con_quartiere.groupby('microgrid')['Energia consumata'].sum().reset_index(name='Energia Totale Consumo (kWh)')

    # Visualizza la tabella dell'energia consumata per microgrid
    st.write("**Energia Totale Consumo per Microgrid**")
    st.write("Il calcolo dell'energia consumata per microgrid è essenziale per valutare le prestazioni energetiche, ottimizzare i costi e pianificare interventi di efficientamento.")
    st.dataframe(energia_per_microgrid, hide_index=True)

