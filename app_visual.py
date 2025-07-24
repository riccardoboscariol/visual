import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json

# Configura Streamlit
st.set_page_config(page_title="Visualizzazione Empatica", layout="wide")
st.title("🌀 Forma Empatica Generativa – Cumulativa")

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

    theta = np.linspace(0, 4 * np.pi, 1000)

    for i, s in enumerate(spirali):
        r = (i + 1) * 0.2 + s["val"] * 0.1
        alpha = min(1.0, 0.3 + s["val"] * 0.1)
        lw = 1 + s["val"] * 0.5

        radius = r * theta
        x = radius * np.cos(theta + i * np.pi / 4)
        y = radius * np.sin(theta + i * np.pi / 4)

        ax.plot(x, y, color=s["color"], alpha=alpha, linewidth=lw)

    st.pyplot(fig)
    st.caption("🌱 L’opera cresce con ogni nuova risposta. Ogni spirale riflette una dimensione empatica.")







