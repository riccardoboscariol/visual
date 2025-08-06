import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import json
import plotly.io as pio
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh
from matplotlib import cm

# 🔄 Aggiornamento automatico ogni 10 secondi
st_autorefresh(interval=10 * 1000, key="refresh")

# 🔧 Configurazione Streamlit
st.set_page_config(page_title="Specchio empatico", layout="wide")
st.title("🌀 Specchio empatico")

# 🔐 Credenziali Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = dict(st.secrets["credentials"])
if isinstance(creds_dict, str):
    creds_dict = json.loads(creds_dict)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("16amhP4JqU5GsGg253F2WJn9rZQIpx1XsP3BHIwXq1EA").sheet1

# 📥 Dati
records = sheet.get_all_records()
df = pd.DataFrame(records)

if df.empty:
    st.warning("Nessuna risposta ancora.")
    st.stop()

# 🌀 Genera spirali per ogni partecipante
fig = go.Figure()
theta = np.linspace(0, 12 * np.pi, 1200)

# Colori per le dimensioni, usati ciclicamente per ogni partecipante
dimensioni = ["PT", "Fantasy", "Empathic Concern", "Personal Distress"]
color_map = {
    "PT": "#e84393",               # fucsia
    "Fantasy": "#e67e22",          # arancio
    "Empathic Concern": "#3498db", # azzurro
    "Personal Distress": "#9b59b6" # viola
}

for idx, row in df.iterrows():
    for i, dim in enumerate(dimensioni):
        valore = row[dim]
        color = color_map[dim]
        intensity = np.clip(valore / 5, 0.2, 1.0)
        r = (i + 1) * 0.25 + idx * 0.03  # Distanza progressiva per ogni spirale/partecipante
        radius = r * (theta / max(theta)) * intensity * 4.5

        x = radius * np.cos(theta + i + idx)
        y = radius * np.sin(theta + i + idx)

        for j in range(1, len(x), 4):
            alpha = 0.2 + 0.7 * (j / len(x))
            fig.add_trace(go.Scatter(
                x=x[j-1:j+1], y=y[j-1:j+1],
                mode="lines",
                line=dict(color=color, width=1.2 + intensity * 2.5),
                opacity=alpha,
                hoverinfo="skip",
                showlegend=False
            ))

# ⚙️ Layout grafico
fig.update_layout(
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    margin=dict(t=0, b=0, l=0, r=0),
    plot_bgcolor='black',
    paper_bgcolor='black',
    autosize=True,
)

# 🔳 Visualizzazione interattiva
html_str = pio.to_html(fig, include_plotlyjs='cdn')
components.html(html_str, height=700, scrolling=False)

# ℹ️ Caption
st.caption("🎨 Le spirali si trasformano ogni 10 secondi, in base alle risposte dei singoli partecipanti. Ogni spirale riflette le qualità empatiche individuali: fantasia, consapevolezza, preoccupazione o angoscia.")

# 📘 Descrizione dell’opera
st.markdown("---")
st.markdown("""
### 🧭 *Empatia come consapevolezza dell’impatto*

> *“L’empatia non è solo sentire l’altro, ma riconoscere il proprio impatto sul mondo e sulla realtà condivisa. È un atto di presenza responsabile.”*

**Breve descrizione:**  
Questa opera esplora l’empatia come dimensione attiva e relazionale della coscienza.  
Andando oltre la semplice risonanza emotiva, propone una visione dell’empatia come capacità di percepire e modulare il proprio effetto sulla realtà.

Le spirali si trasformano continuamente, leggendo i punteggi raccolti dai partecipanti.  
Ogni spirale rappresenta un individuo, e il colore riflette la forza relativa delle diverse qualità empatiche: fantasia, consapevolezza, preoccupazione o angoscia.
""")


