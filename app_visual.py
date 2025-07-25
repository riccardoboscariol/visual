import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import json
import plotly.io as pio
import streamlit.components.v1 as components

st.set_page_config(page_title="Visualizzazione Empatica", layout="wide")
st.title("🌀 Forma Empatica Interattiva – HTML Embed")

# 🔁 Credenziali Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = dict(st.secrets["credentials"])
if isinstance(creds_dict, str):
    creds_dict = json.loads(creds_dict)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("16amhP4JqU5GsGg253F2WJn9rZQIpx1XsP3BHIwXq1EA").sheet1

# 📥 Carica dati
records = sheet.get_all_records()
df = pd.DataFrame(records)

if df.empty:
    st.warning("Nessuna risposta ancora.")
    st.stop()

# 📊 Calcolo medie
pt = df["PT"].mean()
fantasy = df["Fantasy"].mean()
concern = df["Empathic Concern"].mean()
distress = df["Personal Distress"].mean()

values = [pt, fantasy, concern, distress]
labels = ["PT", "Fantasy", "Concern", "Distress"]
colors = ["#3498db", "#9b59b6", "#e67e22", "#e84393"]

# 🌀 Spirali animate
fig = go.Figure()
theta = np.linspace(0, 8 * np.pi, 1000)

for i, val in enumerate(values):
    intensity = np.clip(val / 5, 0.2, 1)
    r = (i + 1) * 0.3
    radius = r * (theta / max(theta)) * intensity * 3

    x = radius * np.cos(theta)
    y = radius * np.sin(theta)

    for j in range(0, len(theta), 5):
        fig.add_trace(go.Scatter(
            x=x[j:j+2], y=y[j:j+2],
            mode="lines",
            line=dict(color=colors[i], width=2 + intensity * 3),
            showlegend=False
        ))

fig.update_layout(
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    margin=dict(t=0, b=0, l=0, r=0),
    plot_bgcolor='black',
    paper_bgcolor='black',
    autosize=True,
)

# ⬇️ Salva come HTML temporaneo
html_str = pio.to_html(fig, include_plotlyjs='cdn')

# ⏬ Mostra il grafico in un iframe
components.html(html_str, height=700, scrolling=False)

st.caption("🌱 Il grafico si aggiorna dinamicamente con ogni nuova risposta. Le spirali riflettono le 4 dimensioni empatiche.")








