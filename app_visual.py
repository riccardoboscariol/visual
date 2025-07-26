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

# 🔁 Auto-refresh
st_autorefresh(interval=10 * 1000, key="refresh")

# 🌌 Configurazione
st.set_page_config(page_title="Specchio Empatico", layout="wide")
st.title("🔄 Specchio Empatico")

# 🔐 Google Sheets
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
    st.warning("Nessuna risposta trovata.")
    st.stop()

# 🧠 Calcolo medie reali
raw_scores = {
    "PT": df["PT"].mean(),
    "Fantasy": df["Fantasy"].mean(),
    "Concern": df["Empathic Concern"].mean(),
    "Distress": df["Personal Distress"].mean()
}

# 🔢 Ordina per valore medio
sorted_dims = sorted(raw_scores.items(), key=lambda x: x[1], reverse=True)

# 🌈 Colormap base
colormaps = [cm.plasma, cm.inferno, cm.viridis, cm.magma]  # Da più vivido a più tenue

# 🔄 Crea lista finale delle spirali (ordinate)
spirali = []
for i, (label, val) in enumerate(sorted_dims):
    spirali.append({
        "label": label,
        "value": val,
        "cmap": colormaps[i],  # Colore assegnato in base all’ordine
        "r_base": (i + 1) * 0.25  # più centrale se valore maggiore
    })

# 📈 Costruisci spirali
fig = go.Figure()
theta = np.linspace(0, 12 * np.pi, 1200)

for i, s in enumerate(spirali):
    val = s["value"]
    normalized = np.clip((val - 1) / 4, 0.2, 1.0)
    r = s["r_base"]
    radius = r * (theta / max(theta)) * 3.2

    x = radius * np.cos(theta + i)
    y = radius * np.sin(theta + i)

    gradient = np.linspace(0, 1, len(x))
    rgba = (s["cmap"](gradient) * 255).astype(int)

    for j in range(1, len(x), 4):
        color = f"rgba({rgba[j][0]}, {rgba[j][1]}, {rgba[j][2]}, {0.3 + 0.5 * normalized:.2f})"
        fig.add_trace(go.Scatter(
            x=x[j-1:j+1],
            y=y[j-1:j+1],
            mode="lines",
            line=dict(color=color, width=1.5 + 3 * normalized),
            showlegend=False,
            hoverinfo="none"
        ))

# Layout grafico
fig.update_layout(
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    margin=dict(t=0, b=0, l=0, r=0),
    plot_bgcolor='black',
    paper_bgcolor='black',
)

# Embed
html_str = pio.to_html(fig, include_plotlyjs='cdn')
components.html(html_str, height=720, scrolling=False)

# Caption interattiva
st.caption("🎨 Le spirali cambiano posizione e colore in base all'importanza relativa (media) delle 4 dimensioni empatiche.")

# 📘 Descrizione dell'opera
st.markdown("---")
st.markdown(
    """
    ### 🧭 *Empatia come consapevolezza dell’impatto*

    > *“L’empatia non è solo sentire l’altro, ma riconoscere il proprio impatto sul mondo e sulla realtà condivisa. È un atto di presenza responsabile.”*

    **Breve descrizione:**  
    Questa opera esplora l’empatia come dimensione attiva e relazionale della coscienza.  
    Andando oltre la semplice risonanza emotiva, propone una visione dell’empatia come capacità di percepire e modulare il proprio effetto sulla realtà.

    **Specchio Empatico** si presenta come una spirale in evoluzione, alimentata dalle risposte dei partecipanti.  
    Le quattro componenti empatiche (Perspective Taking, Fantasy, Empathic Concern, Personal Distress) si intrecciano visivamente  
    e cambiano colore, posizione e forma a seconda del loro peso relativo.  
    L’opera si aggiorna in tempo reale, riflettendo la qualità empatica del collettivo in continua trasformazione.
    """,
    unsafe_allow_html=True
)




