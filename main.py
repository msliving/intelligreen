import streamlit as st
import requests
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import shape
from folium import GeoJson
import random



def aggiungi_strade_alla_mappa(mappa, gdf):
    # Filtra le strade con affluenza "alta"
    gdf_high_affluence = gdf[gdf['affluenza'] == 'alta']

    # Aggiungi le strade alla mappa
    for _, feature in gdf_high_affluence.iterrows():
        # Imposta il colore in base all'affluenza
        color = 'red' if feature['affluenza'] == 'alta' else 'blue'

        folium.GeoJson(
            feature.geometry,
            style_function=lambda x, color=color: {
                'color': color,
                'weight': 5,
                'opacity': 1,
            },
            tooltip=feature['nomevia'],  # Mostra il nome della via al passaggio del mouse
        ).add_to(mappa)

st.title("Mappa Bologna")
left, right = st.columns(2)
col_empty1, col1, col2, col3, col_empty2 = st.columns([2, 2, 2, 2, 1])

# Titolo dell'applicazione


# Carica i file GeoJSON
quartieri_file = 'dati\quartieri.geojson'       # File GeoJSON dei quartieri
zone_file = 'dati\zone.geojson'                 # File GeoJSON delle zone
aree_file = 'dati\\aree-statistiche.geojson'     # File GeoJSON delle aree
lampioni_file = 'dati\lampioni.geojson'         # File GeoJSON dei lampioni
strade_file = 'dati\strade.geojson'             # File GeoJSON delle strade

data_quartieri = pd.read_csv("dati\dati_quartieri.csv", delimiter=',')
data_zone = pd.read_csv("dati\dati_zone.csv", delimiter=',')


st.session_state.gdf_quartieri = gpd.read_file(quartieri_file)
st.session_state.gdf_zone = gpd.read_file(zone_file)
st.session_state.gdf_aree = gpd.read_file(aree_file)
st.session_state.gdf_lampioni = gpd.read_file(lampioni_file)
st.session_state.gdf_arcs = gpd.read_file(strade_file)
gdf_quartieri = st.session_state.gdf_quartieri
gdf_zone = st.session_state.gdf_zone
gdf_aree = st.session_state.gdf_aree
gdf_lampioni = st.session_state.gdf_lampioni
gdf_arcs = st.session_state.gdf_arcs

bologna_coords = [44.490, 11.430]
show_quartieri = col1.checkbox("**Quartieri**", value=True)
show_lampioni = col2.checkbox("**Lampioni**", value=False)
show_strade = col3.checkbox("**Strade**", value=False)



# Funzione per generare un colore casuale
def random_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

# Carica i dati GeoJSON
@st.cache_data
def load_color():
    gdf_quartieri['color'] = [random_color() for _ in range(len(gdf_quartieri))]
    gdf_zone['color'] = [random_color() for _ in range(len(gdf_zone))]
    gdf_aree['color'] = [random_color() for _ in range(len(gdf_aree))]
    
    return gdf_quartieri, gdf_zone, gdf_aree

# Carica i dati una sola volta
gdf_quartieri, gdf_zone, gdf_aree = load_color()

def name(selected_option):
    if selected_option == 'Aree Statistiche':
        aliases=['Area Statistica:']
    elif selected_option == 'Quartieri':
        aliases=['Quartiere:']
    elif selected_option == 'Zone':
        aliases=['Zona:']
    return aliases

# Funzione per creare una mappa Folium
def create_map(gdf_quartieri, gdf_zone, gdf_aree, selected_option, show_quartieri):
    # Inizializza la mappa centrata su Bologna
    m = folium.Map(location=[44.490, 11.430], zoom_start=12, zoom_control=True, scrollWheelZoom=True, dragging=True)

    # Aggiungi i dati GeoJSON in base all'opzione selezionata, se il checkbox è selezionato
    if show_quartieri and selected_option is not None:
        if selected_option == 'Aree Statistiche':
            geojson_data = gdf_aree[['geometry', 'area_statistica', 'color']]
            name_column = 'area_statistica'  # Colonna per il nome
        elif selected_option == 'Quartieri':
            geojson_data = gdf_quartieri[['geometry', 'quartiere', 'color']]
            name_column = 'quartiere'  # Colonna per il nome
        elif selected_option == 'Zone':
            geojson_data = gdf_zone[['geometry', 'zona_fiu', 'color']]
            name_column = 'zona_fiu'  # Colonna per il nome

        # Funzione per stilizzare il GeoJson
        def style_function(feature):
            return {
                'fillColor': feature['properties']['color'],
                'color': 'black',  # Colore del bordo
                'weight': 1.5,     # Spessore del bordo
                'fillOpacity': 0.6  # Opacità del riempimento
            }

        # Aggiungi il GeoJSON alla mappa con stile
        geojson = GeoJson(
            geojson_data,
            style_function=style_function,
            highlight_function=lambda x: {
                'fillColor': x['properties']['color'],  # Colore di evidenziazione al passaggio del mouse
                'color': 'black',        # Colore del bordo
                'weight': 2,             # Spessore del bordo
                'fillOpacity': 0.9       # Opacità del riempimento
            },
            tooltip=folium.GeoJsonTooltip(
                fields=[name_column],  # Colonne da mostrare nel tooltip
                aliases= name(selected_option),  # Etichette per i campi
                localize=True
            )
        )

        geojson.add_to(m)

    return m

with st.sidebar:
    # Disabilita i radio button se il checkbox è attivo
    if show_quartieri:
        selected_option = st.radio("Seleziona il tipo di area da visualizzare:", 
                                   ['Quartieri','Zone','Aree Statistiche'])
    else:
        selected_option = None


mappa = create_map(gdf_quartieri, gdf_zone, gdf_aree, selected_option, show_quartieri)


if show_lampioni:
        # Itera attraverso i lampioni per aggiungere marker colorati
        for _, row in gdf_lampioni.iterrows():
            # Determina il colore dell'icona in base allo stato del lampione
            if row['Stato'] == 'Funzionante':
                color = 'green'  # Colore verde per funzionanti
            else:
                color = 'red'  # Colore rosso per guasti

            # Aggiungi il marker per ogni lampione
            folium.Marker(
                location=[row.geometry.y, row.geometry.x],  # Coordinate (lat, lon)
                icon=folium.Icon(color=color, icon='lightbulb', prefix='fa'),  # Icona lampione
                tooltip=folium.Tooltip(
                    f"Tipo: {row['Tipo']}<br>"
                    f"Tecnologia: {row['Tecnologia']}<br>"
                    f"Intensità Luminosa: {row['Intensità luminosa']} lm<br>"
                    f"Energia Cons.: {row['Energia consumata']} W<br>"
                    f"Stato: {row['Stato']}"
                )
            ).add_to(mappa)

if show_strade:
    aggiungi_strade_alla_mappa(mappa, gdf_arcs)

# Crea la mappa in base alla selezione e al valore del checkbox

st_folium(mappa, width=1800, height=600)

st.dataframe(data_quartieri, hide_index=True)
st.dataframe(data_zone, hide_index=True)

st.subheader("Meteo Bologna, IT")
col_empty21, col21, col22, col23, col_empty22 = st.columns([1, 2, 2, 2, 1])

def get_weather():
    # Parametri della richiesta
    params = {
        'q': "Bologna", #City name
        'appid': "635ea302891e58a9b64729c6441f45e3", #API key
        'units': 'metric',  # Per ottenere la temperatura in Celsius
        'lang': 'it'  # Per ricevere la descrizione meteo in italiano
    }
    # Richiesta ai server di OpenWeatherMap
    response = requests.get("http://api.openweathermap.org/data/2.5/weather", params=params)

    # Se la richiesta ha avuto successo, parsifica i dati JSON
    if response.status_code == 200:
        data = response.json()
        return {
            'description': data['weather'][0]['description'],
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'],
            'city': data['name'],
            'country': data['sys']['country']
        }
    else:
        st.error("Errore: città non trovata o problema con l'API.")
        return None

weather_data = get_weather()
if weather_data:
    # Output dei dati meteo
    col21.write(f"Descrizione: {weather_data['description'].capitalize()}")
    col22.write(f"Temperatura: {weather_data['temperature']}°C")
    col23.write(f"Umidità: {weather_data['humidity']}%")
