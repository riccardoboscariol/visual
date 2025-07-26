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

# 🔧 Configurazione pagina
st.set_page_config(page_title="Specchio empatico", layout="wide")
st.title("Specchio empatico")

# 🔐 Credenziali Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = dict(st.secrets["credentials"])
if isinstance(creds_dict, str):
    creds_dict = json.loads(creds_dict)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("16amhP4JqU5GsGg253F2WJn9rZQIpx1XsP3BHIwXq1EA").sheet1

# 📥 Carica dati SENZA cache
df = pd.DataFrame(sheet.get_all_records())
st.write("DEBUG – Numero righe lette da Google Sheets:", df.shape[0])

if df.empty:
    st.warning("Nessuna risposta registrata.")
    st.stop()

# 📊 Punteggi medi
pt = df["PT"].mean()
fantasy = df["Fantasy"].mean()
concern = df["Empathic Concern"].mean()
distress = df["Personal Distress"].mean()

st.write("Valori medi letti:", pt, fantasy, concern, distress)

values = [pt, fantasy, concern, distress]
labels = ["PT", "Fantasy", "Concern", "Distress"]

# 🎨 Colormap psichedelica
colormaps = [cm.plasma, cm.magma, cm.inferno, cm.viridis]

# 🔁 Esagerazione visiva
def exaggerate(val):
    norm = np.clip(val / 5, 0, 1)
    return np.clip((norm ** 2.5) * 3.5, 0.3, 4.0)  # amplifica differenze piccole

# 🎥 Spirali
fig = go.Figure()
theta = np.linspace(0, 12 * np.pi, 1200)

for i, (val, cmap) in enumerate(zip(values, colormaps)):
    intensity = exaggerate(val)
    r = (i + 1) * 0.3
    radius = r * (theta / max(theta)) * intensity

    x = radius * np.cos(theta + i)
    y = radius * np.sin(theta + i)

    # Gradiente di colore con trasparenza
    normalized = np.linspace(0, 1, len(x))
    rgba = cmap(normalized)
    rgba = (rgba * 255).astype(int)

    for j in range(1, len(x), 4):
        color = f"rgba({rgba[j][0]}, {rgba[j][1]}, {rgba[j][2]}, {0.3 + 0.6 * normalized[j]:.2f})"
        fig.add_trace(go.Scatter(
            x=x[j-1:j+1],
            y=y[j-1:j+1],
            mode="lines",
            line=dict(color=color, width=1.5 + intensity),
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

# HTML interattivo
html_str = pio.to_html(fig, include_plotlyjs='cdn')
components.html(html_str, height=720, scrolling=False)

# 📘 Descrizione
st.caption("🌀 Le spirali reagiscono ai punteggi cumulativi al test, con modifiche esagerate nella geometria e trasparenze. L’opera evolve ogni 10 secondi.")

st.markdown("---")
st.markdown(
    """
    ### 🧭 *Empatia come consapevolezza dell’impatto*

    > *“L’empatia non è solo sentire l’altro, ma riconoscere il proprio impatto sul mondo e sulla realtà condivisa. È un atto di presenza responsabile.”*

    **Breve descrizione:**  
    Questa opera esplora l’empatia come dimensione attiva e relazionale della coscienza.  
    Andando oltre la semplice risonanza emotiva, propone una visione dell’empatia come capacità di percepire e modulare il proprio effetto sulla realtà.
    """,
    unsafe_allow_html=True
)






