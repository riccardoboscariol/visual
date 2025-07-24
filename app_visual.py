import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json

# Configura la pagina
st.set_page_config(page_title="Visualizzazione Empatica", layout="wide")
st.title("🌀 Forma Empatica Generativa")

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

# Carica le risposte
records = sheet.get_all_records()
df = pd.DataFrame(records)

# Ultima riga
if not df.empty:
    last = df.iloc[-1]

    # Estrai i punteggi
    pt = last["PT"]
    fantasy = last["Fantasy"]
    concern = last["Empathic Concern"]
    distress = last["Personal Distress"]

    # Inizia generazione artistica
    st.subheader("🌈 Forma basata sull'empatia")
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect('equal')
    ax.axis('off')

    # Parametri normalizzati
    n_bracci = int(round(pt)) + 2
    ampiezza = fantasy / 2
    colori = ['#FF6B6B', '#6BCB77', '#4D96FF', '#FFC75F']
    alpha = min(max(concern / 7, 0.2), 0.9)
    intensità = distress * 5

    # Disegno spirali dinamiche con "movimento"
    for i in range(n_bracci):
        t = np.linspace(0, 4 * np.pi, 400)
        r = ampiezza * t
        r_mod = r + np.sin(3 * t + i) * 0.3 * (distress / 5)  # effetto movimento
        x = r_mod * np.cos(t + i * 2 * np.pi / n_bracci)
        y = r_mod * np.sin(t + i * 2 * np.pi / n_bracci)
        ax.plot(x, y, alpha=alpha, linewidth=2.5, color=colori[i % len(colori)])

    # Auto-zoom per non tagliare nulla
    limite = (ampiezza + 1.5) * intensità
    ax.set_xlim(-limite, limite)
    ax.set_ylim(-limite, limite)

    st.pyplot(fig)

else:
    st.warning("Non ci sono ancora risposte registrate nel foglio Google Sheets.")


