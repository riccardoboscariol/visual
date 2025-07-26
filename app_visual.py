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
from matplotlib import cm

# 🔄 Auto-refresh ogni 10 secondi
st_autorefresh(interval=10 * 1000, key="refresh")

# Configurazione pagina
st.set_page_config(page_title="Specchio empatico", layout="wide")
st.title("🌀 Specchio Empatico – Versione Armoniosa")

# Credenziali
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = dict(st.secrets["credentials"])
if isinstance(creds_dict, str):
    creds_dict = json.loads(creds_dict)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("16amhP4JqU5GsGg253F2WJn9rZQIpx1XsP3BHIwXq1EA").sheet1

# Dati dal foglio
records = sheet.get_all_records()
df = pd.DataFrame(records)

if df.empty:
    st.warning("Nessuna risposta registrata.")
    st.stop()

# Calcolo medie reali
pt = df["PT"].mean()
fantasy = df["Fantasy"].mean()
concern = df["Empathic Concern"].mean()
distress = df["Personal Distress"].mean()

# 🔍 Normalizzazione tra 1 e 5
scores = [pt, fantasy, concern, distress]
labels = ["PT", "Fantasy", "Concern", "Distress"]
colormaps = [cm.plasma, cm.magma, cm.inferno, cm.viridis]

# Spirali
theta = np.linspace(0, 12 * np.pi, 1200)
fig = go.Figure()

for i, (val, cmap) in enumerate(zip(scores, colormaps)):
    normalized = np.clip((val - 1) / 4, 0.2, 1.0)
    r_base = (i + 1) * 0.3
    radius = r_base * (theta / max(theta)) * 2.5

    x = radius * np.cos(theta + i)
    y = radius * np.sin(theta + i)

    gradient = np.linspace(0, 1, len(x))
    rgba = (cmap(gradient) * 255).astype(int)

    for j in range(1, len(x), 4):
        color = f"rgba({rgba[j][0]}, {rgba[j][1]}, {rgba[j][2]}, {0.3 + 0.5 * normalized:.2f})"
        fig.add_trace(go.Scatter(
            x=x[j-1:j+1],
            y=y[j-1:j+1],
            mode="lines",
            line=dict(color=color, width=1.5 + 3 * normalized),
            showlegend=False,
            hoverinfo="none"
        ))

# Layout grafico
fig.update_layout(
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    margin=dict(t=0, b=0, l=0, r=0),
    plot_bgcolor='black',
    paper_bgcolor='black',
)

# Embed grafico HTML
html_str = pio.to_html(fig, include_plotlyjs='cdn')
components.html(html_str, height=720, scrolling=False)

# Caption
st.caption("🌱 Ogni spirale rappresenta una dimensione empatica. L’intensità e i colori cambiano con le medie cumulative del test.")

# Descrizione sotto
st.markdown("---")
st.markdown(
    """
    ### 🧭 *Empatia come consapevolezza dell’impatto*

    > *“L’empatia non è solo sentire l’altro, ma riconoscere il proprio impatto sul mondo e sulla realtà condivisa. È un atto di presenza responsabile.”*

    **Breve descrizione:**  
    Questa opera esplora l’empatia come dimensione attiva e relazionale della coscienza.  
    Andando oltre la semplice risonanza emotiva, propone una visione dell’empatia come capacità di percepire e modulare il proprio effetto sulla realtà.
    """
)






