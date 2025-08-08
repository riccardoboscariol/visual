import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np
import json
import random
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

# 🎨 Colori per dimensione dominante
dimension_colors = {
    "PT": "#e84393",               # fucsia
    "Fantasy": "#e67e22",          # arancio
    "Empathic Concern": "#3498db", # azzurro
    "Personal Distress": "#9b59b6" # viola
}

theta = np.linspace(0, 12 * np.pi, 600)  # meno punti → più leggero
spirali = []

for idx, row in df.iterrows():
    media = np.mean([row["PT"], row["Fantasy"], row["Empathic Concern"], row["Personal Distress"]])

    # Trova dimensione dominante
    punteggi = {
        "PT": row["PT"],
        "Fantasy": row["Fantasy"],
        "Empathic Concern": row["Empathic Concern"],
        "Personal Distress": row["Personal Distress"]
    }
    max_score = max(punteggi.values())
    max_dims = [dim for dim, val in punteggi.items() if val == max_score]
    dominant_dimension = random.choice(max_dims)  # in caso di pareggio sceglie a caso

    color = dimension_colors[dominant_dimension]

    intensity = np.clip(media / 5, 0.2, 1.0)
    freq = 0.5 + (media / 5) * (3.0 - 0.5)  # Hz

    r = 0.3 + idx * 0.08
    radius = r * (theta / max(theta)) * intensity * 4.5

    x = radius * np.cos(theta + idx)
    y = radius * np.sin(theta + idx)

    # Inclinazione alternata
    if idx % 2 == 0:
        y_proj = y * 0.5 + x * 0.2
    else:
        y_proj = y * 0.5 - x * 0.2

    spirali.append({
        "x": x.tolist(),
        "y": y_proj.tolist(),
        "color": color,
        "intensity": float(intensity),
        "freq": float(freq)
    })

# Centratura verticale
all_y = np.concatenate([np.array(s["y"]) for s in spirali])
y_min, y_max = all_y.min(), all_y.max()
OFFSET = -0.06 * (y_max - y_min)
for s in spirali:
    s["y"] = (np.array(s["y"]) + OFFSET).tolist()

data_json = json.dumps({"spirali": spirali})

# 📊 HTML + JS
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
let t0 = Date.now();
let traces = [];
const step = 4;

// Creazione iniziale dei traces (statici)
DATA.spirali.forEach(s => {{
    for(let j=1; j < s.x.length; j += step){{
        traces.push({{
            x: s.x.slice(j-1, j+1),
            y: s.y.slice(j-1, j+1),
            mode: "lines",
            line: {{color: s.color, width: 1.5 + s.intensity * 3}},
            opacity: 0.5,
            hoverinfo: "none",
            showlegend: false,
            type: "scatter",
            freq: s.freq,
            pos: j / s.x.length
        }});
    }}
}});

const layout = {{
    xaxis: {{visible: false, autorange: true, scaleanchor: 'y'}},
    yaxis: {{visible: false, autorange: true}},
    margin: {{t:0,b:0,l:0,r:0}},
    paper_bgcolor: 'black',
    plot_bgcolor: 'black',
    autosize: true
}};

Plotly.newPlot('graph', traces, layout, {{
    displayModeBar: false,
    scrollZoom: false,
    responsive: true
}});

// Animazione leggera a 30fps
function animate(){{
    const time = (Date.now() - t0) / 1000;
    const newOpacities = traces.map(tr => {{
        const flicker = 0.5 + 0.5 * Math.sin(2 * Math.PI * tr.freq * time);
        return Math.max(0, (0.2 + 0.7 * tr.pos) * flicker);
    }});
    Plotly.restyle('graph', {{opacity: [newOpacities]}});
    setTimeout(animate, 33); // ~30 fps
}}
animate();

// Fullscreen button
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








