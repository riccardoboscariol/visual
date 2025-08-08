import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import json
import colorsys
import time

# 📌 Auto-refresh ogni 10 secondi
st.set_page_config(page_title="Specchio empatico", layout="wide")
st.markdown("""
    <style>
    html, body, [class*="css"] {
        margin: 0;
        padding: 0;
        height: 100%;
        width: 100%;
        background-color: black;
        overflow: hidden;
    }
    .block-container {
        padding: 0 !important;
    }
    iframe {
        height: 100vh !important;
        width: 100vw !important;
    }
    :fullscreen {
        cursor: none;
    }
    </style>
""", unsafe_allow_html=True)

# 🔐 Credenziali Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = dict(st.secrets["credentials"])
if isinstance(creds_dict, str):
    creds_dict = json.loads(creds_dict)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("16amhP4JqU5GsGg253F2WJn9rZQIpx1XsP3BHIwXq1EA").sheet1

# 📥 Lettura dati
records = sheet.get_all_records()
df = pd.DataFrame(records)
if df.empty:
    st.warning("Nessuna risposta ancora.")
    st.stop()

# 🎨 Mappatura base colori (dimensione dominante → colore base HEX)
dimension_colors = {
    "PT": "#e84393",               # fucsia
    "Fantasy": "#e67e22",          # arancio
    "Empathic Concern": "#3498db", # azzurro
    "Personal Distress": "#9b59b6" # viola
}

# 🎯 Funzione per modificare luminosità/saturazione
def adjust_color(hex_color, factor):
    # hex → rgb
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    # rgb → hls
    h, l, s = colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)
    # modifica luminosità in base al fattore
    l = min(1.0, l * factor)
    s = min(1.0, s * factor)
    # hls → rgb
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return '#%02x%02x%02x' % (int(r*255), int(g*255), int(b*255))

# 🌀 Preparazione spirali
fig = go.Figure()
theta = np.linspace(0, 12 * np.pi, 1200)
timestamp = time.time()

for idx, row in df.iterrows():
    # punteggio medio
    media = np.mean([row["PT"], row["Fantasy"], row["Empathic Concern"], row["Personal Distress"]])
    
    # trova dimensione dominante
    dominant_dimension = max(
        ["PT", "Fantasy", "Empathic Concern", "Personal Distress"],
        key=lambda dim: row[dim]
    )
    base_color = dimension_colors[dominant_dimension]
    
    # fattore per saturazione/luminosità (da 0.6 a 1.2)
    color_factor = 0.6 + (media / 5) * 0.6
    final_color = adjust_color(base_color, color_factor)

    # intensità per spessore linea
    intensity = np.clip(media / 5, 0.2, 1.0)

    # raggio base
    r = 0.3 + idx * 0.08
    radius = r * (theta / max(theta)) * intensity * 4.5

    x = radius * np.cos(theta + idx)
    y = radius * np.sin(theta + idx)

    # inclinazione alternata
    if idx % 2 == 0:
        y_proj = y * 0.5 + x * 0.2
    else:
        y_proj = y * 0.5 - x * 0.2

    # sfarfallio in base al punteggio medio
    freq = 0.5 + (media / 5) * (3.0 - 0.5)  # Hz
    phase = np.sin(2 * np.pi * freq * timestamp)

    for j in range(1, len(x), 4):
        alpha = (0.2 + 0.7 * (j / len(x))) * (0.5 + 0.5 * phase)
        fig.add_trace(go.Scatter(
            x=x[j-1:j+1],
            y=y_proj[j-1:j+1],
            mode="lines",
            line=dict(color=final_color, width=1.5 + intensity * 3),
            opacity=max(0, alpha),
            hoverinfo="none",
            showlegend=False
        ))

# ⚙️ Layout grafico
fig.update_layout(
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    margin=dict(t=0, b=0, l=0, r=0),
    plot_bgcolor='black',
    paper_bgcolor='black',
    autosize=True,
    height=1000,
    width=2000
)

# 🔳 Mostra grafico
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# 📘 Descrizione
st.markdown("---")
st.markdown("""
### 🧭 *Empatia come consapevolezza dell’impatto*

Ogni spirale rappresenta un partecipante.
- **Colore base** → dimensione empatica dominante.
- **Luminosità/Saturazione** → proporzionale al punteggio medio (più alto → colore più brillante).
- **Sfarfallio** → più veloce con punteggi medi alti.

L'opera evolve in tempo reale con l'arrivo di nuove risposte.
""")

