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

# Autenticazione Google Sheets
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
    # Calcola le medie cumulative
    pt = df["PT"].mean()
    fantasy = df["Fantasy"].mean()
    concern = df["Empathic Concern"].mean()
    distress = df["Personal Distress"].mean()

    # Parametri grafici
    colors = {
        "PT": "#3498db",         # blu
        "Fantasy": "#9b59b6",    # viola
        "Concern": "#e67e22",    # arancio
        "Distress": "#e84393"    # rosa
    }

    values = {
        "PT": pt,
        "Fantasy": fantasy,
        "Concern": concern,
        "Distress": distress
    }

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect('equal')
    ax.axis('off')

    # Disegna cerchi concentrici, uno per ogni sottoscala
    max_radius = 1.0
    for i, (label, val) in enumerate(values.items()):
        base_radius = max_radius
        linewidth = 2 + val * 1.5  # aumenta lo spessore
        alpha = min(1.0, 0.3 + val * 0.1)

        circle = plt.Circle(
            (0, 0),
            radius=base_radius - i * 0.15,
            color=colors[label],
            fill=False,
            linewidth=linewidth,
            alpha=alpha,
            label=label
        )
        ax.add_patch(circle)

    # Legenda
    ax.legend(loc="upper right", frameon=False, fontsize=10)

    # Rendering
    st.pyplot(fig)
    st.caption("✨ Ogni cerchio rappresenta una dimensione empatica. Colore e spessore variano con l'intensità media delle risposte.")




