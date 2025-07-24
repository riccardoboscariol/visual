import streamlit as st
import gspread
import json
import pandas as pd
import plotly.graph_objs as go
from oauth2client.service_account import ServiceAccountCredentials

# --- Autenticazione Google Sheets ---
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds_dict = dict(st.secrets["credentials"])
if isinstance(creds_dict, str):
    creds_dict = json.loads(creds_dict)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# --- Apri Sheet
SHEET_ID = "16amhP4JqU5GsGg253F2WJn9rZQIpx1XsP3BHIwXq1EA"
try:
    sheet = client.open_by_key(SHEET_ID).sheet1
except Exception:
    st.error("Errore accesso a Google Sheet — controlla credenziali e permessi.")
    st.stop()

# --- Carica dati
records = sheet.get_all_records()
if not records:
    st.warning("Nessuna risposta trovata.")
    st.stop()

df = pd.DataFrame(records)

# --- Estrai l’ultima riga (ultima risposta)
latest = df.tail(1).iloc[0]

# --- IRI: colonne finali con punteggi
iri_cols = ["Perspective Taking", "Fantasy", "Empathic Concern", "Personal Distress"]
iri_scores = {col: latest.get(col) for col in iri_cols}

st.header("🧠 Forma empatica generata")
st.write("Ultima risposta ricevuta alle:", latest["timestamp"] if "timestamp" in latest else "—")

# --- Grafico radar con Plotly
categories = list(iri_scores.keys())
values = list(iri_scores.values())
values += values[:1]  # chiusura grafico

fig = go.Figure(
    data=[
        go.Scatterpolar(r=values, theta=categories + [categories[0]],
                        fill="toself", name="IRI Scores",
                        line_color="mediumblue")
    ],
    layout=go.Layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        showlegend=False
    )
)
st.plotly_chart(fig, use_container_width=True)

# --- Interazione personalizzata
st.subheader("🎨 Personalizza la tua forma")
color = st.color_picker("Scegli un colore per la forma", "#4455aa")
scale = st.slider("Scala dimensione", 0.5, 2.0, 1.0)

fig.update_traces(fillcolor=color, line_color=color)
fig.update_layout(width=int(400 * scale), height=int(400 * scale))
st.plotly_chart(fig, use_container_width=True)

# --- Download immagine
st.plotly_chart(fig, use_container_width=True)
st.download_button("📥 Scarica immagine", data=img_bytes, file_name="forma_empatica.png", mime="image/png")
