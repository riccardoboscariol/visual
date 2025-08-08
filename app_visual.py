import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np
import json
import time

# ───────────────────────────────
# CONFIGURAZIONE STREAMLIT
# ───────────────────────────────
st.set_page_config(page_title="Specchio empatico", layout="wide")

# CSS per full screen e nascondere cursore
st.markdown("""
    <style>
    html, body, [class*="css"] {
        margin: 0;
        padding: 0;
        height: 100%;
        width: 100%;
        background-color: black;
        overflow: hidden;
        cursor: none;
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

# ───────────────────────────────
# LETTURA DATI DA GOOGLE SHEETS
# ───────────────────────────────
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = dict(st.secrets["credentials"])
if isinstance(creds_dict, str):
    creds_dict = json.loads(creds_dict)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("16amhP4JqU5GsGg253F2WJn9rZQIpx1XsP3BHIwXq1EA").sheet1

records = sheet.get_all_records()
df = pd.DataFrame(records)

if df.empty:
    st.warning("Nessuna risposta ancora.")
    st.stop()

# ───────────────────────────────
# PREPARAZIONE DATI PER JAVASCRIPT
# ───────────────────────────────
theta = np.linspace(0, 12 * np.pi, 1200)
palette = {
    "PT": "#e84393",  # fucsia
    "Fantasy": "#e67e22",  # arancio
    "Empathic Concern": "#3498db",  # azzurro
    "Personal Distress": "#9b59b6"  # viola
}

spirali_data = []

for idx, row in df.iterrows():
    # Colore in base alla dimensione dominante
    dominant_dim = max(["PT", "Fantasy", "Empathic Concern", "Personal Distress"], key=lambda col: row[col])
    base_color = palette[dominant_dim]

    # Intensità in base alla media
    media = np.mean([row["PT"], row["Fantasy"], row["Empathic Concern"], row["Personal Distress"]])
    intensity = np.clip(media / 5, 0.2, 1.0)

    # Geometria spirale
    r = 0.3 + idx * 0.08
    radius = r * (theta / max(theta)) * intensity * 4.5
    x = radius * np.cos(theta + idx)
    y = radius * np.sin(theta + idx)

    # Inclinazione alternata
    if idx % 2 == 0:
        y_proj = y * 0.5 + x * 0.2
    else:
        y_proj = y * 0.5 - x * 0.2

    spirali_data.append({
        "x": x.tolist(),
        "y": y_proj.tolist(),
        "color": base_color,
        "intensity": float(intensity),
        "delay": idx * 0.1,  # ritardo animazione per effetto onda
        "flickerSpeed": 0.5 + (media / 5) * 1.5  # velocità sfarfallio dopo apertura
    })

# ───────────────────────────────
# JAVASCRIPT PER ANIMAZIONE
# ───────────────────────────────
spirali_json = json.dumps({"theta": theta.tolist(), "spirali": spirali_data})

js_code = f"""
<div id="plot" style="width:100vw;height:100vh;"></div>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<script>
const data = {spirali_json};
const traces = [];
const totalFrames = 60; // durata animazione apertura ~1s a 60fps

data.spirali.forEach((spirale, i) => {{
    traces.push({{
        x: [spirale.x[0]],
        y: [spirale.y[0]],
        mode: "lines",
        line: {{ color: spirale.color, width: 1.5 + spirale.intensity * 3 }},
        opacity: 1,
        hoverinfo: "none",
        showlegend: false
    }});
}});

const layout = {{
    xaxis: {{ visible: false }},
    yaxis: {{ visible: false }},
    margin: {{ t:0, b:0, l:0, r:0 }},
    paper_bgcolor: "black",
    plot_bgcolor: "black"
}};

Plotly.newPlot('plot', traces, layout, {{displayModeBar: false}});

let frame = 0;
function animate() {{
    frame++;
    const update = {{x: [], y: [], opacity: []}};
    data.spirali.forEach((spirale, i) => {{
        const progress = Math.min(1, Math.max(0, (frame/totalFrames) - spirale.delay));
        const pointsToShow = Math.floor(progress * spirale.x.length);
        update.x.push(spirale.x.slice(0, pointsToShow));
        update.y.push(spirale.y.slice(0, pointsToShow));

        if (progress >= 1) {{
            const flicker = 0.2 + 0.7 * (0.5 + 0.5 * Math.sin(Date.now()/200 * spirale.flickerSpeed));
            update.opacity.push(flicker);
        }} else {{
            update.opacity.push(1);
        }}
    }});
    Plotly.update('plot', update, {{}});
    requestAnimationFrame(animate);
}}

animate();
</script>
"""

# ───────────────────────────────
# MOSTRA GRAFICO
# ───────────────────────────────
st.components.v1.html(js_code, height=1000, scrolling=False)



