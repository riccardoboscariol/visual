import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import json
import plotly.io as pio
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

# 🔄 Auto-refresh ogni 10 secondi
st_autorefresh(interval=10 * 1000, key="auto_refresh")

# 🔧 Configurazione pagina
st.set_page_config(page_title="Visualizzazione Empatica", layout="wide")
st.title("🌀 Forma Empatica Interattiva – HTML Embed")

# 🔐 Credenziali
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

# 🌀 Spirali animate con variazione più evidente
fig = go.Figure()
theta = np.linspace(0, 10 * np.pi, 1000)

for i, val in enumerate(values):
    intensity = np.clip(val / 5, 0.3, 1.0)
    r = (i + 1) * 0.3
    radius = r * (theta / max(theta)) * intensity * 4.5  # amplificato

    x = radius * np.cos(theta + i)
    y = radius * np.sin(theta + i)

    for j in range(0, len(theta) - 1, 6):
        fig.add_trace(go.Scatter(
            x=x[j:j+2], y=y[j:j+2],
            mode="lines",
            line=dict(
                color=colors[i],
                width=2 + intensity * 5,
                dash="dash" if val < 3 else "solid"
            ),
            hoverinfo="none",
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

# 💾 Embed HTML in app
html_str = pio.to_html(fig, include_plotlyjs='cdn')
components.html(html_str, height=720, scrolling=False)

st.caption("🌱 Le spirali si aggiornano ogni 10 secondi. L'intensità, il colore e lo stile cambiano in base alle medie empatiche.")







