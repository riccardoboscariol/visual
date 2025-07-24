import streamlit as st
from streamlit_autorefresh import st_autorefresh
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json

# Configura Streamlit
st.set_page_config(page_title="Visualizzazione Empatica", layout="wide")
st.title("🌀 Forma Empatica Generativa – Cumulativa")

# 🔄 Auto-refresh ogni 20 secondi
st_autorefresh(interval=20000, key="auto_refresh")

# Autenticazione
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = dict(st.secrets["credentials"])
if isinstance(creds_dict, str):
    creds_dict = json.loads(creds_dict)

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("16amhP4JqU5GsGg253F2WJn9rZQIpx1XsP3BHIwXq1EA").sheet1

# Carica dati
records = sheet.get_all_records()
df = pd.DataFrame(records)

if df.empty:
    st.warning("Nessun dato ancora registrato.")
else:
    # Calcola le medie
    pt = df["PT"].mean()
    fantasy = df["Fantasy"].mean()
    concern = df["Empathic Concern"].mean()
    distress = df["Personal Distress"].mean()

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal')
    ax.axis('off')

    spirali = [
        {"val": pt, "color": "#3498db"},       # PT - blu
        {"val": fantasy, "color": "#9b59b6"},  # Fantasy - viola
        {"val": concern, "color": "#e67e22"},  # EC - arancio
        {"val": distress, "color": "#e84393"}  # PD - rosa
    ]

    max_raggio = 2.8  # cerchio contenitore
    theta = np.linspace(0, 4 * np.pi, 800)

    for i, s in enumerate(spirali):
        intensità = np.clip(s["val"] / 5, 0, 1)  # normalizza
        fade = np.linspace(0.3, 1.0, len(theta)) * intensità

        r = (i + 1) * 0.25
        radius = r * (theta / max(theta))
        radius *= max_raggio * (0.4 + 0.6 * intensità)  # amplifica dinamica

        x = radius * np.cos(theta + i * np.pi / 2)
        y = radius * np.sin(theta + i * np.pi / 2)

        for j in range(1, len(x)):
            ax.plot(
                x[j - 1:j + 1],
                y[j - 1:j + 1],
                color=s["color"],
                alpha=fade[j],
                linewidth=2 + 4 * intensità
            )

    st.pyplot(fig)
    st.caption("🌱 Ogni spirale rappresenta una dimensione empatica. L’intensità e l’ampiezza crescono con le medie cumulative.")









