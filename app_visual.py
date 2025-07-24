import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json

# Configura la pagina
st.set_page_config(page_title="Forma Empatica", layout="wide")
st.title("🌌 Visualizzazione Generativa Empatica")

# Autenticazione Google Sheets
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = dict(st.secrets["credentials"])
if isinstance(creds_dict, str):
    creds_dict = json.loads(creds_dict)

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("16amhP4JqU5GsGg253F2WJn9rZQIpx1XsP3BHIwXq1EA").sheet1

# Carica i dati
records = sheet.get_all_records()
df = pd.DataFrame(records)

# Verifica presenza dati
if not df.empty:
    last = df.iloc[-1]

    try:
        pt = float(last["PT"])
        fantasy = float(last["Fantasy"])
        concern = float(last["Empathic Concern"])
        distress = float(last["Personal Distress"])
    except KeyError as e:
        st.error(f"Colonna mancante: {e}")
        st.stop()

    # Parametri derivati normalizzati
    n_bracci = int(round(pt)) + 2
    ampiezza = fantasy / 2
    colori = ['#FF6B6B', '#6BCB77', '#4D96FF', '#FFC75F']
    alpha = min(max(concern / 7, 0.2), 0.9)  # safe clamp
    intensità = distress * 5


    # Disegna spirale generativa
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_facecolor("black")
    ax.axis("off")

    t = np.linspace(0, 2 * np.pi * n_bracci, 1000)
    r = 1 + ampiezza * np.sin(intensità * t)

    for i in range(4):
        x = r * np.cos(t + i * np.pi/2)
        y = r * np.sin(t + i * np.pi/2)
        ax.plot(x, y, alpha=alpha, linewidth=2.5, color=colori[i])

    # Cerchi concentrici come base
    for i in range(1, 5):
        circle = plt.Circle((0, 0), i, edgecolor="white", fill=False, alpha=0.1)
        ax.add_patch(circle)

    st.pyplot(fig)

else:
    st.warning("Non ci sono ancora risposte nel foglio.")


