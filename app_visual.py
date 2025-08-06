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

# 🔄 Aggiornamento automatico ogni 10 secondi
st_autorefresh(interval=10 * 1000, key="refresh")

# 🔧 Configurazione Streamlit
st.set_page_config(page_title="Specchio empatico", layout="wide")

# 🔧 Rimuove padding e margini
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        margin: 0;
        padding: 0;
        height: 100%;
        width: 100%;
        background-color: black;
    }
    .block-container {
        padding: 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

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

# 🎨 Palette colori
palette = ["#e84393", "#e67e22", "#3498db", "#9b59b6"]

# 🌀 Genera spirali 3D per ogni partecipante
fig = go.Figure()
theta = np.linspace(0, 8 * np.pi, 800)

for idx, row in df.iterrows():
    media = np.mean([row["PT"], row["Fantasy"], row["Empathic Concern"], row["Personal Distress"]])
    color = palette[idx % len(palette)]
    intensity = np.clip(media / 5, 0.2, 1.0)

    r = 1 + idx * 0.2  # distanza progressiva
    x = r * np.cos(theta + idx)
    y = r * np.sin(theta + idx)
    z = theta * intensity * 0.5  # spirale lungo z

    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z,
        mode='lines',
        line=dict(color=color, width=2 + intensity * 3),
        opacity=0.7,
        hoverinfo='skip',
        showlegend=False
    ))

# ⚙️ Layout 3D
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        bgcolor='black'
    ),
    margin=dict(t=0, b=0, l=0, r=0),
    paper_bgcolor='black',
    plot_bgcolor='black',
)

# 🔳 Visualizzazione interattiva fullscreen
html_str = f"""
<div style="position:fixed; top:0; left:0; width:100vw; height:100vh; overflow:hidden; z-index:0;">
    {pio.to_html(fig, include_plotlyjs='cdn', full_html=False, config={"displayModeBar": False})}
</div>
"""
components.html(html_str, height=900, scrolling=False)

# ℹ️ Caption
st.markdown("""<br><br><br><br>""", unsafe_allow_html=True)
st.caption("🎨 Le spirali tridimensionali si rigenerano ogni 10 secondi, riflettendo le qualità empatiche individuali di ciascun partecipante.")

# 📘 Descrizione dell’opera
st.markdown("---")
st.markdown("""
### 🧭 *Empatia come consapevolezza dell’impatto*

> *“L’empatia non è solo sentire l’altro, ma riconoscere il proprio impatto sul mondo e sulla realtà condivisa. È un atto di presenza responsabile.”*

**Breve descrizione:**  
Questa opera esplora l’empatia come dimensione attiva e relazionale della coscienza.  
Andando oltre la semplice risonanza emotiva, propone una visione dell’empatia come capacità di percepire e modulare il proprio effetto sulla realtà.

Ogni spirale tridimensionale rappresenta un partecipante.  
La traiettoria, l’intensità e il colore emergono dai suoi punteggi nelle diverse qualità empatiche: fantasia, consapevolezza, preoccupazione o angoscia.
""")




