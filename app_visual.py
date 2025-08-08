import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np
import json
import time

# ─────────────────────────────
# CONFIGURAZIONE STREAMLIT
# ─────────────────────────────
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

# ─────────────────────────────
# CONNESSIONE A GOOGLE SHEETS
# ─────────────────────────────
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = dict(st.secrets["credentials"])
if isinstance(creds_dict, str):
    creds_dict = json.loads(creds_dict)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("16amhP4JqU5GsGg253F2WJn9rZQIpx1XsP3BHIwXq1EA").sheet1

# ─────────────────────────────
# ENDPOINT PER DATI AGGIORNATI
# ─────────────────────────────
# Se l'URL contiene ?data=1, ritorna solo i dati in JSON
query_params = st.query_params
if "data" in query_params:
    records = sheet.get_all_records()
    df = pd.DataFrame(records)

    if df.empty:
        st.json([])
    else:
        palette = ["#e84393", "#e67e22", "#3498db", "#9b59b6"]
        spirali = []
        theta = np.linspace(0, 12 * np.pi, 1200).tolist()

        for idx, row in df.iterrows():
            media = np.mean([row["PT"], row["Fantasy"], row["Empathic Concern"], row["Personal Distress"]])
            intensity = np.clip(media / 5, 0.2, 1.0)
            r = 0.3 + idx * 0.08
            radius = (r * (np.array(theta) / max(theta)) * intensity * 4.5).tolist()
            color = palette[idx % len(palette)]

            x = (np.array(radius) * np.cos(np.array(theta) + idx)).tolist()
            y = (np.array(radius) * np.sin(np.array(theta) + idx)).tolist()

            if idx % 2 == 0:
                y_proj = (np.array(y) * 0.5 + np.array(x) * 0.2).tolist()
            else:
                y_proj = (np.array(y) * 0.5 - np.array(x) * 0.2).tolist()

            spirali.append({
                "x": x,
                "y": y_proj,
                "color": color,
                "intensity": intensity
            })

        st.json({"theta": theta, "spirali": spirali})
    st.stop()

# ─────────────────────────────
# HTML + JAVASCRIPT PER GRAFICO DINAMICO
# ─────────────────────────────
html_code = """
<!DOCTYPE html>
<html>
<head>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<style>
body { margin:0; background:black; overflow:hidden; }
#graph { width:100vw; height:100vh; }
</style>
</head>
<body>
<div id="graph"></div>
<script>
async function fetchData(){
    const resp = await fetch(window.location.href + "?data=1");
    return await resp.json();
}

async function drawGraph(){
    const data = await fetchData();
    const traces = [];

    data.spirali.forEach(s => {
        const step = 4;
        for(let j=1; j < s.x.length; j += step){
            const alpha = 0.2 + 0.7 * (j / s.x.length);
            traces.push({
                x: s.x.slice(j-1, j+1),
                y: s.y.slice(j-1, j+1),
                mode: "lines",
                line: {color: s.color, width: 1.5 + s.intensity * 3},
                opacity: alpha,
                hoverinfo: "none",
                showlegend: false,
                type: "scatter"
            });
        }
    });

    const layout = {
        xaxis: {visible: false},
        yaxis: {visible: false},
        margin: {t:0,b:0,l:0,r:0},
        paper_bgcolor: 'black',
        plot_bgcolor: 'black'
    };

    Plotly.newPlot('graph', traces, layout, {displayModeBar: false});
}

// Primo disegno
drawGraph();

// Aggiornamento ogni 10 secondi senza ricreare il grafico
setInterval(async () => {
    const data = await fetchData();
    const traces = [];

    data.spirali.forEach(s => {
        const step = 4;
        for(let j=1; j < s.x.length; j += step){
            const alpha = 0.2 + 0.7 * (j / s.x.length);
            traces.push({
                x: s.x.slice(j-1, j+1),
                y: s.y.slice(j-1, j+1),
                mode: "lines",
                line: {color: s.color, width: 1.5 + s.intensity * 3},
                opacity: alpha,
                hoverinfo: "none",
                showlegend: false,
                type: "scatter"
            });
        }
    });

    Plotly.react('graph', traces, {
        xaxis: {visible: false},
        yaxis: {visible: false},
        margin: {t:0,b:0,l:0,r:0},
        paper_bgcolor: 'black',
        plot_bgcolor: 'black'
    }, {displayModeBar: false});
}, 10000);
</script>
</body>
</html>
"""

st.components.v1.html(html_code, height=800, scrolling=False)

# ─────────────────────────────
# DESCRIZIONI STATICHE
# ─────────────────────────────
st.caption("🎨 Le spirali si rigenerano ogni 10 secondi con effetto 'respiro'. Ogni spirale rappresenta un partecipante.")
st.markdown("---")
st.markdown("""
### 🧭 *Empatia come consapevolezza dell’impatto*

> *“L’empatia non è solo sentire l’altro, ma riconoscere il proprio impatto sul mondo e sulla realtà condivisa. È un atto di presenza responsabile.”*

**Breve descrizione:**  
Ogni spirale rappresenta un individuo.  
L'inclinazione alternata e il respiro collettivo creano un'opera viva, che evolve al ritmo delle risposte.
""")







