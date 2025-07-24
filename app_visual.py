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

    # Punteggi → raggi
    radii = [pt, fantasy, concern, distress]
    colors = ['#6baed6', '#9e9ac8', '#fd8d3c', '#f768a1']
    labels = ["PT", "Fantasy", "Concern", "Distress"]

    # Cerchi concentrici
    for i, r in enumerate(sorted(radii, reverse=True)):
        circle = plt.Circle((0, 0), r * 0.6, color=colors[i], alpha=0.4, label=labels[i])
        ax.add_patch(circle)

    # Legenda
    ax.legend(loc="upper right")

    st.pyplot(fig)

else:
    st.warning("Non ci sono ancora risposte registrate nel foglio Google Sheets.")

