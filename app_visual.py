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

# 🎨 Colori base per dimensione
dimension_colors = {
    "PT": "#e84393",
    "Fantasy": "#e67e22",
    "Empathic Concern": "#3498db",
    "Personal Distress": "#9b59b6"
}

theta = np.linspace(0, 12 * np.pi, 1200)
spirali = []

for idx, row in df.iterrows():
    punteggi = {
        "PT": row["PT"],
        "Fantasy": row["Fantasy"],
        "Empathic Concern": row["Empathic Concern"],
        "Personal Distress": row["Personal Distress"]
    }
    max_val = max(punteggi.values())
    dimensioni_max = [dim for dim, val in punteggi.items() if val == max_val]
    dominante = random.choice(dimensioni_max)

    color = dimension_colors[dominante]

    media = np.mean(list(punteggi.values()))
    intensity = np.clip(media / 5, 0.2, 1.0)
    freq = 0.5 + (media / 5) * (3.0 - 0.5)

    r = 0.3 + idx * 0.08
    radius = r * (theta / max(theta)) * intensity * 4.5

    x = radius * np.cos(theta + idx)
    y = radius * np.sin(theta + idx)

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

# 📏 Offset verticale per centratura
all_y = np.concatenate([np.array(s["y"]) for s in spirali])
y_min, y_max = all_y.min(), all_y.max()
y_range = y_max - y_min
OFFSET = -0.06 * y_range
for s in spirali:
    s["y"] = (np.array(s["y"]) + OFFSET).tolist()

data_json = json.dumps({"spirali": spirali})

# 📊 HTML + JS ottimizzato
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

// Creiamo le tracce una sola volta
const step = 4;
let traces = [];
DATA.spirali.forEach(s => {{
    for(let j=1; j < s.x.length; j += step){{
        const alpha = 0; // inizialmente trasparenti
        traces.push({{
            x: s.x.slice(j-1, j+1),
            y: s.y.slice(j-1, j+1),
            mode: "lines",
            line: {{color: s.color, width: 1.5 + s.intensity * 3}},
            opacity: alpha,
            hoverinfo: "none",
            showlegend: false,
            type: "scatter"
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

let t0 = Date.now();
setInterval(() => {{
    const time = (Date.now() - t0) / 1000;
    let newOpacities = [];
    let index = 0;
    DATA.spirali.forEach(s => {{
        const flicker = 0.5 + 0.5 * Math.sin(2 * Math.PI * s.freq * time);
        for(let j=1; j < s.x.length; j += step){{
            const alpha = (0.2 + 0.7 * (j / s.x.length)) * flicker;
            newOpacities[index] = Math.max(0, alpha);
            index++;
        }}
    }});
    Plotly.restyle('graph', {{opacity: [newOpacities]}});
}}, 40); // ~25 fps

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

st.caption("🎨 Premi ⛶ per il fullscreen totale. Colore = scala dominante, casuale in caso di pareggio. Sfarfallio proporzionale al punteggio medio.")






