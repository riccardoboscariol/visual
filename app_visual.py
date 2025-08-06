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
import time

# 🔄 Auto-refresh continuo ogni 10 secondi
st_autorefresh(interval=10 * 1000, key="auto-refresh")

# 🔧 Config layout
st.set_page_config(page_title="Specchio empatico", layout="wide")

# 🔧 Rimuovi padding e imposta full screen
st.markdown("""
    <style>
    html, body, [class*="css"] {
        margin: 0;
        padding: 0;
        height: 100%;
        width: 100%;
        background-color: black;
        overflow: hidden;
    }
    .block-container {
        padding: 0 !important;
    }
    iframe {
        height: 100vh !important;
        width: 100vw !important;
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

# ⏱️ Calcola fase "respiro"
timestamp = time.time()
time_offset = (timestamp % 10) / 10  # da 0 a 1
breath_scale = 1 + 0.08 * np.sin(2 * np.pi * time_offset)  # respiro

# 🌀 Spirali con respiro e inclinazione alternata
fig = go.Figure()
theta = np.linspace(0, 12 * np.pi, 1200)

for idx, row in df.iterrows():
    media = np.mean([row["PT"], row["Fantasy"], row["Empathic Concern"], row["Personal Distress"]])
    intensity = np.clip(media / 5, 0.2, 1.0)
    r = 0.3 + idx * 0.08
    radius = r * (theta / max(theta)) * intensity * 4.5 * breath_scale
    color = palette[idx % len(palette)]

    x = radius * np.cos(theta + idx)
    y = radius * np.sin(theta + idx)

    # Alterna inclinazione: destra ↔ sinistra
    if idx % 2 == 0:
        y_proj = y * 0.5 + x * 0.2
    else:
        y_proj = y * 0.5 - x * 0.2

    for j in range(1, len(x), 4):
        alpha = 0.2 + 0.7 * (j / len(x))
        fig.add_trace(go.Scatter(
            x=x[j-1:j+1],
            y=y_proj[j-1:j+1],
            mode="lines",
            line=dict(color=color, width=1.5 + intensity * 3),
            opacity=alpha,
            hoverinfo="none",
            showlegend=False
        ))

# ⚙️ Layout a schermo intero
fig.update_layout(
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    margin=dict(t=0, b=0, l=0, r=0),
    plot_bgcolor='black',
    paper_bgcolor='black',
    autosize=True,
    height=1000,
    width=2000
)

# 🔳 Visualizzazione a schermo intero
html_str = pio.to_html(fig, include_plotlyjs='cdn', full_html=False, config={"displayModeBar": False})
components.html(html_str, height=1000, scrolling=False)

# ℹ️ Caption
st.caption("🎨 Le spirali respirano ogni 10 secondi, con inclinazione alternata. Ogni partecipante genera un vortice unico e dinamico.")

# 📘 Descrizione dell’opera
st.markdown("---")
st.markdown("""
### 🧭 *Empatia come consapevolezza dell’impatto*

> *“L’empatia non è solo sentire l’altro, ma riconoscere il proprio impatto sul mondo e sulla realtà condivisa. È un atto di presenza responsabile.”*

**Breve descrizione:**  
Questa opera esplora l’empatia come dimensione attiva e relazionale della coscienza.  
Ogni spirale rappresenta un individuo.  
Le loro inclinazioni alternate e il respiro collettivo creano un campo visivo in movimento, come un organismo fatto di connessioni empatiche vive.
""")







