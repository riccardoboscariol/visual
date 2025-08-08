import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np
import json
from streamlit_autorefresh import st_autorefresh

# 🔄 Auto-refresh ogni 10 secondi
st_autorefresh(interval=10000, key="refresh")

# 🖥 Configurazione Streamlit
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
    </style>
""", unsafe_allow_html=True)

# 🔐 Connessione Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = dict(st.secrets["credentials"])
if isinstance(creds_dict, str):
    creds_dict = json.loads(creds_dict)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("16amhP4JqU5GsGg253F2WJn9rZQIpx1XsP3BHIwXq1EA").sheet1

# 📥 Dati
records = sheet.get_all_records()
df = pd.DataFrame(records)
if df.empty:
    st.warning("Nessuna risposta ancora.")
    st.stop()

# 🎨 Colori fissi per scala
dimension_colors = {
    "PT": "#e84393",               # fucsia
    "Fantasy": "#e67e22",          # arancio
    "Empathic Concern": "#3498db", # azzurro
    "Personal Distress": "#9b59b6" # viola
}

# 🔧 Parametri spirali
theta = np.linspace(0, 12 * np.pi, 1200)
TIE_SPREAD = 0.03  # 3% di variazione di raggio tra spirali duplicate (pareggio)

spirali = []

for idx, row in df.iterrows():
    # Punteggi e media
    scores = {
        "PT": row["PT"],
        "Fantasy": row["Fantasy"],
        "Empathic Concern": row["Empathic Concern"],
        "Personal Distress": row["Personal Distress"]
    }
    media = float(np.mean(list(scores.values())))
    intensity = float(np.clip(media / 5, 0.2, 1.0))
    freq = float(0.5 + (media / 5) * (3.0 - 0.5))  # Hz per sfarfallio

    # Geometria base (senza tie-offset)
    r = 0.3 + idx * 0.08
    base_radius = r * (theta / max(theta)) * intensity * 4.5
    base_x = base_radius * np.cos(theta + idx)
    base_y = base_radius * np.sin(theta + idx)

    # Inclinazione alternata
    if idx % 2 == 0:
        base_y_proj = base_y * 0.5 + base_x * 0.2
    else:
        base_y_proj = base_y * 0.5 - base_x * 0.2

    # Dominanti (gestione pareggi → più spirali)
    max_val = max(scores.values())
    dominant_dims = [dim for dim, val in scores.items() if val == max_val]
    t = len(dominant_dims)

    for k, dim in enumerate(dominant_dims):
        # scala di raggio per separare visivamente spirali duplicate (centrate)
        # esempi: t=2 -> scale: [-0.015, +0.015]; t=3 -> [-0.03, 0, +0.03]
        scale = 1.0 + (k - (t - 1) / 2.0) * TIE_SPREAD

        x = (base_x * scale).tolist()
        y_proj = (base_y_proj * scale).tolist()

        spirali.append({
            "x": x,
            "y": y_proj,
            "color": dimension_colors[dim],
            "intensity": intensity,
            "freq": freq
        })

# 📏 Offset verticale per centratura visiva
all_y = np.concatenate([np.array(s["y"]) for s in spirali])
y_min, y_max = all_y.min(), all_y.max()
y_range = y_max - y_min
OFFSET = -0.06 * y_range
for s in spirali:
    s["y"] = (np.array(s["y"]) + OFFSET).tolist()

data_json = json.dumps({"spirali": spirali})

# 📊 HTML + JS (render una volta, poi aggiorna solo opacità a 25fps) + fullscreen
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
body {{ margin:0; background:black; overflow:hidden; }}
#graph {{ width:100vw; height:100vh; position:relative; }}
#fullscreen-btn {{
    position: absolute;
    top: 10px; right: 10px;
    z-index: 9999;
    background: rgba(255,255,255,0.2);
    color: white;
    border: none;
    padding: 6px 10px;
    border-radius: 5px;
    cursor: pointer;
    font-size: 18px;
}}
#fullscreen-btn:hover {{
    background: rgba(255,255,255,0.4);
}}
:fullscreen {{
    cursor: none;
}}
</style>
</head>
<body>
<button id="fullscreen-btn">⛶</button>
<div id="graph"></div>
<script>
const DATA = {data_json};

// Costruiamo le tracce una sola volta (segmenti) per performance
const step = 4;
let traces = [];
DATA.spirali.forEach(s => {{
    for (let j = 1; j < s.x.length; j += step) {{
        traces.push({{
            x: s.x.slice(j-1, j+1),
            y: s.y.slice(j-1, j+1),
            mode: "lines",
            line: {{ color: s.color, width: 1.5 + s.intensity * 3 }},
            opacity: 0,  // inizialmente trasparenti; le accendiamo sotto
            hoverinfo: "none",
            showlegend: false,
            type: "scatter"
        }});
    }}
}});

const layout = {{
    xaxis: {{ visible: false, autorange: true, scaleanchor: 'y' }},
    yaxis: {{ visible: false, autorange: true }},
    margin: {{ t:0, b:0, l:0, r:0 }},
    paper_bgcolor: 'black',
    plot_bgcolor: 'black',
    autosize: true
}};

Plotly.newPlot('graph', traces, layout, {{
    displayModeBar: false,
    scrollZoom: false,
    responsive: true
}});

// Aggiorniamo SOLO l'opacità a ~25fps per ridurre carico
let t0 = Date.now();
const updateIntervalMs = 40;

setInterval(() => {{
    const time = (Date.now() - t0) / 1000;
    let newOpacities = new Array(traces.length);
    let index = 0;

    DATA.spirali.forEach(s => {{
        // sfarfallio in base a freq del partecipante (costante per i duplicati)
        const flicker = 0.5 + 0.5 * Math.sin(2 * Math.PI * s.freq * time);
        for (let j = 1; j < s.x.length; j += step) {{
            const baseAlpha = 0.2 + 0.7 * (j / s.x.length);
            newOpacities[index] = Math.max(0, baseAlpha * flicker);
            index++;
        }}
    }});

    Plotly.restyle('graph', {{ opacity: [newOpacities] }});
}}, updateIntervalMs);

// Fullscreen
document.getElementById('fullscreen-btn').addEventListener('click', () => {{
    const graphDiv = document.getElementById('graph');
    if (graphDiv.requestFullscreen) graphDiv.requestFullscreen();
    else if (graphDiv.webkitRequestFullscreen) graphDiv.webkitRequestFullscreen();
    else if (graphDiv.msRequestFullscreen) graphDiv.msRequestFullscreen();
}});
</script>
</body>
</html>
"""

st.components.v1.html(html_code, height=800, scrolling=False)

# ℹ️ Caption + descrizione
st.caption("🎨 Pareggi senza aleatorietà: per ogni scala a pari merito nasce una spirale, con piccoli scarti concentrici. Pulsante ⛶ per fullscreen.")
st.markdown("---")
st.markdown("""
### 🧭 *Empatia come consapevolezza dell’impatto*
Ogni spirale rappresenta un individuo; in caso di pareggio tra scale dominanti, ne vedi più di una, una per ciascuna scala, con colore dedicato e lieve scarto radiale.
Lo sfarfallio resta proporzionale al punteggio medio.
""")







