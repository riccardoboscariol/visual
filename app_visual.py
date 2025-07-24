import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
from streamlit_autorefresh import st_autorefresh

# Auto-refresh ogni 30s
st_autorefresh(interval=30 * 1000, key="refresh")

# Config Streamlit
st.set_page_config(page_title="Visualizzazione Empatica – Animata", layout="wide")
st.title("🌪️ Spirali Empatiche Dinamiche")

# Autenticazione
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = dict(st.secrets["credentials"])
if isinstance(creds_dict, str):
    creds_dict = json.loads(creds_dict)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("16amhP4JqU5GsGg253F2WJn9rZQIpx1XsP3BHIwXq1EA").sheet1

# Caricamento dati
records = sheet.get_all_records()
df = pd.DataFrame(records)

if df.empty:
    st.warning("Nessun dato ancora registrato.")
else:
    # Medie per sottoscala
    pt = df["PT"].mean()
    fantasy = df["Fantasy"].mean()
    concern = df["Empathic Concern"].mean()
    distress = df["Personal Distress"].mean()

    global_mean = np.mean([pt, fantasy, concern, distress])
    direction = 1 if global_mean > 3.5 else -1  # Rotazione oraria/antioraria

    spirali = [
        {"val": pt, "color": "#3498db", "label": "PT"},
        {"val": fantasy, "color": "#9b59b6", "label": "Fantasy"},
        {"val": concern, "color": "#e67e22", "label": "Concern"},
        {"val": distress, "color": "#e84393", "label": "Distress"},
    ]

    fig = go.Figure()
    theta = np.linspace(0, 4 * np.pi, 800)

    for i, s in enumerate(spirali):
        intensity = np.clip(s["val"] / 5, 0, 1)
        base_radius = (i + 1) * 0.3
        radius = base_radius * (theta / max(theta)) * 2.5 * intensity

        x = radius * np.cos(direction * theta + i * np.pi / 2)
        y = radius * np.sin(direction * theta + i * np.pi / 2)

        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode="lines",
            line=dict(color=s["color"], width=2 + 3 * intensity),
            name=s["label"],
            opacity=0.7
        ))

    fig.update_layout(
        showlegend=True,
        height=800,
        width=800,
        margin=dict(l=0, r=0, t=40, b=40),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )

    st.plotly_chart(fig, use_container_width=True)
    st.caption("🌀 Ogni spirale rappresenta una dimensione empatica. L'intensità e la direzione dipendono dai valori medi cumulativi.")






