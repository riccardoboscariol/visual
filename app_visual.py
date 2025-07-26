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

# 📊 Calcolo delle medie
medie = {
    "PT": df["PT"].mean(),
    "Fantasy": df["Fantasy"].mean(),
    "Empathic Concern": df["Empathic Concern"].mean(),
    "Personal Distress": df["Personal Distress"].mean()
}

# 🎨 Colori in ordine di "importanza" (dalla media più alta alla più bassa)
palette = ["#e84393", "#e67e22", "#3498db", "#9b59b6"]  # fucsia, arancio, azzurro, viola

# 🔢 Ordina dimensioni per media (dalla più alta)
dimensioni_ordinate = sorted(medie.items(), key=lambda x: x[1], reverse=True)

# 🌀 Genera spirali
fig = go.Figure()
theta = np.linspace(0, 12 * np.pi, 1200)

for i, (nome, media) in enumerate(dimensioni_ordinate):
    color = palette[i]
    intensity = np.clip(media / 5, 0.2, 1.0)
    r = (i + 1) * 0.25
    radius = r * (theta / max(theta)) * intensity * 4.5

    x = radius * np.cos(theta + i)
    y = radius * np.sin(theta + i)

    for j in range(1, len(x), 4):
        alpha = 0.2 + 0.7 * (j / len(x))
        fig.add_trace(go.Scatter(
            x=x[j-1:j+1], y=y[j-1:j+1],
            mode="lines",
            line=dict(color=color, width=1.5 + intensity * 3),
            opacity=alpha,
            hoverinfo="none",
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
st.caption("🎨 Le spirali si trasformano ogni 10 secondi, in base alle risposte cumulative. Ogni colore riflette la forza relativa delle dimensioni empatiche.")

# 📘 Descrizione dell’opera
st.markdown("---")
st.markdown("""
### 🧭 *Empatia come consapevolezza dell’impatto*

> *“L’empatia non è solo sentire l’altro, ma riconoscere il proprio impatto sul mondo e sulla realtà condivisa. È un atto di presenza responsabile.”*

**Breve descrizione:**  
Questa opera esplora l’empatia come dimensione attiva e relazionale della coscienza.  
Andando oltre la semplice risonanza emotiva, propone una visione dell’empatia come capacità di percepire e modulare il proprio effetto sulla realtà.

Le spirali si trasformano continuamente, leggendo i punteggi raccolti dai partecipanti.  
Il colore di ogni spirale viene ridefinito in tempo reale in base al predominio delle diverse qualità empatiche: fantasia, consapevolezza, preoccupazione o angoscia.
""")


