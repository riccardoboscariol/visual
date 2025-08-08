import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import json
import time

# 🔧 Configurazione Streamlit
st.set_page_config(page_title="Specchio empatico", layout="wide")

# 🔧 Stile full screen e no padding
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
    </style>
""", unsafe_allow_html=True)

# 🔐 Connessione a Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = dict(st.secrets["credentials"])
if isinstance(creds_dict, str):
    creds_dict = json.loads(creds_dict)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("16amhP4JqU5GsGg253F2WJn9rZQIpx1XsP3BHIwXq1EA").sheet1

# 🎨 Palette colori
palette = ["#e84393", "#e67e22", "#3498db", "#9b59b6"]

# 🌀 Funzione per generare la figura
def genera_figura(df):
    timestamp = time.time()
    time_offset = (timestamp % 10) / 10
    breath_scale = 1 + 0.08 * np.sin(2 * np.pi * time_offset)

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

    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(t=0, b=0, l=0, r=0),
        plot_bgcolor='black',
        paper_bgcolor='black',
        autosize=True,
        height=900
    )
    return fig

# 📌 Placeholder grafico
grafico_placeholder = st.empty()

# 📄 Testo fisso sotto il grafico
st.caption("🎨 Le spirali si rigenerano ogni 10 secondi con effetto 'respiro'. Ogni spirale rappresenta un partecipante.")
st.markdown("---")
st.markdown("""
### 🧭 *Empatia come consapevolezza dell’impatto*

> *“L’empatia non è solo sentire l’altro, ma riconoscere il proprio impatto sul mondo e sulla realtà condivisa. È un atto di presenza responsabile.”*

**Breve descrizione:**  
Ogni spirale rappresenta un individuo.  
L'inclinazione alternata e il respiro collettivo creano un'opera viva, che evolve al ritmo delle risposte.
""")

# 📌 Loop aggiornamento in-place
if "last_row_count" not in st.session_state:
    st.session_state.last_row_count = 0

while True:
    records = sheet.get_all_records()
    df = pd.DataFrame(records)

    if not df.empty:
        if len(df) != st.session_state.last_row_count:
            st.session_state.last_row_count = len(df)

        fig = genera_figura(df)
        with grafico_placeholder:
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    else:
        grafico_placeholder.warning("Nessuna risposta ancora.")

    time.sleep(10)  # Aggiorna ogni 10 secondi










