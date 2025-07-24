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

# 🔄 Auto-refresh ogni 15 secondi
st_autorefresh(interval=15000, key="auto_refresh")

st.title("🌀 Forma Empatica Generativa – Cumulativa")

# Autenticazione Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = dict(st.secrets["credentials"])
if isinstance(creds_dict, str):
    creds_dict = json.loads(creds_dict)

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("16amhP4JqU5GsGg253F2WJn9rZQIpx1XsP3BHIwXq1EA").sheet1

# Carica i dati
records = sheet.get_all_records()
df = pd.DataFrame(records)

if df.empty:
    st.warning("Nessun dato ancora registrato.")
else:
    # Medie cumulative
    pt = df["PT"].mean()
    fantasy = df["Fantasy"].mean()
    concern = df["Empathic Concern"].mean()
    distress = df["Personal Distress"].mean()

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal')
    ax.axis('off')

    spirali = [
        {"val": pt, "color": "#3498db"},
        {"val": fantasy, "color": "#9b59b6"},
        {"val": concern, "color": "#e67e22"},
        {"val": distress, "color": "#e84393"}
    ]

    theta = np.linspace(0, 6 * np.pi, 1000)

    for i, s in enumerate(spirali):
        base_radius = 1.0  # stesso raggio base per tutti
        radius_variation = 0.2 * s["val"]
        radius = base_radius + radius_variation

        alpha = min(1.0, 0.3 + s["val"] * 0.1)
        lw = 1 + s["val"] * 0.5

        r = radius * np.ones_like(theta)
        x = r * np.cos(theta + i * np.pi / 4)
        y = r * np.sin(theta + i * np.pi / 4)

        # Colore con gradiente
        for j in range(len(theta) - 1):
            frac = j / len(theta)
            ax.plot(
                x[j:j+2],
                y[j:j+2],
                color=s["color"],
                alpha=alpha * (0.5 + 0.5 * frac),
                linewidth=lw
            )

    st.pyplot(fig)
    st.caption("🌱 L’opera cresce con ogni nuova risposta. Le spirali rappresentano le dimensioni empatiche in evoluzione.")








