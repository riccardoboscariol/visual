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

# 🔄 Refresh automatico ogni 10 secondi
st_autorefresh(interval=10 * 1000, key="auto_refresh")

# Configurazione Streamlit
st.set_page_config(page_title="Specchio empatico", layout="wide")
st.title("🌀 Specchio empatico – visualizzazione dinamica")

# 🔐 Credenziali Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = dict(st.secrets["credentials"])
if isinstance(creds_dict, str):
    creds_dict = json.loads(creds_dict)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("16amhP4JqU5GsGg253F2WJn9rZQIpx1XsP3BHIwXq1EA").sheet1

# 📥 Dati dal foglio
records = sheet.get_all_records()
df = pd.DataFrame(records)

if df.empty:
    st.warning("Nessuna risposta registrata.")
    st.stop()

# Calcolo delle medie cumulative
pt = df["PT"].mean()
fantasy = df["Fantasy"].mean()
concern = df["Empathic Concern"].mean()
distress = df["Personal Distress"].mean()

values = [pt, fantasy, concern, distress]
labels = ["PT", "Fantasy", "Concern", "Distress"]
colormaps = [cm.plasma, cm.magma, cm.inferno, cm.viridis]

# 📈 Figura
fig = go.Figure()
theta = np.linspace(0, 14 * np.pi, 1200)
media_globale = np.mean(values)
rotazione = 1 if media_globale > 3.2 else -1

for i, (val, cmap) in enumerate(zip(values, colormaps)):
    intensity = np.clip(val / 5, 0.2, 1.2)
    larghezza = 2 + 5 * intensity
    opacita_base = 0.2 + 0.7 * intensity

    r_base = (i + 1) * 0.25
    radius = r_base * (theta / max(theta)) * intensity * 5

    deformazione = 1 + 0.3 * np.sin(3 * theta + i)
    radius *= deformazione

    x = radius * np.cos(theta * rotazione + i)
    y = radius * np.sin(theta * rotazione + i)

    normalized = np.linspace(0, 1, len(x))
    rgba = cmap(normalized)
    rgba = (rgba * 255).astype(int)

    for j in range(1, len(x), 3):
        color = f"rgba({rgba[j][0]}, {rgba[j][1]}, {rgba[j][2]}, {opacita_base:.2f})"
        fig.add_trace(go.Scatter(
            x=x[j-1:j+1], y=y[j-1:j+1],
            mode="lines",
            line=dict(color=color, width=larghezza),
            hoverinfo="none",
            showlegend=False
        ))

# Layout
fig.update_layout(
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    margin=dict(t=0, b=0, l=0, r=0),
    plot_bgcolor='black',
    paper_bgcolor='black',
    autosize=True,
)

# Mostra embed interattivo
html_str = pio.to_html(fig, include_plotlyjs='cdn')
components.html(html_str, height=720, scrolling=False)

# Caption e descrizione
st.caption("🌱 Le spirali reagiscono ai punteggi cumulativi: si deformano, ruotano, si espandono. L’opera evolve ogni 10 secondi.")

st.markdown("---")
st.markdown("""
### 🧭 *Empatia come consapevolezza dell’impatto*

> *“L’empatia non è solo sentire l’altro, ma riconoscere il proprio impatto sul mondo e sulla realtà condivisa. È un atto di presenza responsabile.”*

**Breve descrizione:**  
Questa opera esplora l’empatia come dimensione attiva e relazionale della coscienza.  
Andando oltre la semplice risonanza emotiva, propone una visione dell’empatia come capacità di percepire e modulare il proprio effetto sulla realtà.
""")






