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

# 🔁 Auto-refresh ogni 10 secondi
st_autorefresh(interval=10 * 1000, key="auto_refresh")

# 🌐 Config pagina
st.set_page_config(page_title="Specchio empatico", layout="wide")
st.title("🌀 Specchio empatico")

# 🔐 Google Sheets Auth
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = dict(st.secrets["credentials"])
if isinstance(creds_dict, str):
    creds_dict = json.loads(creds_dict)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("16amhP4JqU5GsGg253F2WJn9rZQIpx1XsP3BHIwXq1EA").sheet1

# 📥 Caricamento dati
records = sheet.get_all_records()
df = pd.DataFrame(records)

if df.empty:
    st.warning("Nessuna risposta registrata.")
    st.stop()

# 📊 Medie punteggi
pt = df["PT"].mean()
fantasy = df["Fantasy"].mean()
concern = df["Empathic Concern"].mean()
distress = df["Personal Distress"].mean()

# 🔧 Esagerazione visiva: enfatizza differenze minime
def exaggerate(val):
    normalized = np.clip(val / 5, 0, 1)
    return normalized ** 1.5  # <--- Modifica esagerata (aumenta contrasto)

values = [pt, fantasy, concern, distress]
scaled_values = [exaggerate(v) for v in values]
labels = ["PT", "Fantasy", "Concern", "Distress"]
colormaps = [cm.plasma, cm.magma, cm.inferno, cm.viridis]

# 🎨 Disegno spirali
fig = go.Figure()
theta = np.linspace(0, 12 * np.pi, 1200)

for i, (val, scale, cmap) in enumerate(zip(values, scaled_values, colormaps)):
    r = (i + 1) * 0.25
    radius = r * (theta / max(theta)) * scale * 5  # <--- visivamente più grande

    x = radius * np.cos(theta + i)
    y = radius * np.sin(theta + i)

    normalized = np.linspace(0, 1, len(x))
    rgba = (cmap(normalized) * 255).astype(int)

    for j in range(1, len(x), 4):
        alpha = 0.2 + 0.6 * scale
        color = f"rgba({rgba[j][0]}, {rgba[j][1]}, {rgba[j][2]}, {alpha:.2f})"
        fig.add_trace(go.Scatter(
            x=x[j-1:j+1], y=y[j-1:j+1],
            mode="lines",
            line=dict(color=color, width=1 + scale * 4),
            hoverinfo="none",
            showlegend=False
        ))

# Layout nero spaziale
fig.update_layout(
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    margin=dict(t=0, b=0, l=0, r=0),
    plot_bgcolor='black',
    paper_bgcolor='black',
    autosize=True,
)

# 📡 Embed HTML
html_str = pio.to_html(fig, include_plotlyjs='cdn')
components.html(html_str, height=720, scrolling=False)

# 📘 Caption + descrizione
st.caption("🔁 Le spirali reagiscono alle medie cumulative, amplificando graficamente anche minimi cambiamenti. L’opera si evolve ogni 10 secondi.")
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






