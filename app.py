import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats

# ─── CONFIG ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Detección de Anomalías",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── COLORES ──────────────────────────────────────────────────────────────────
COLOR_NORMAL   = "#22D3EE"
COLOR_ALERTA   = "#818CF8"
COLOR_ANOMALIA = "#A855F7"
COLOR_PRIMARY  = "#080818"
COLOR_ACCENT   = "#818CF8"
COLOR_BG       = "#0D1340"
COLOR_CARD     = "#0B0B20"

TIPO_COLORS = {
    "Normal":   COLOR_NORMAL,
    "Alerta":   COLOR_ALERTA,
    "Anomalia": COLOR_ANOMALIA
}

# ─── HELPER: DataFrame → HTML tabla oscura ────────────────────────────────────
def df_to_html(df, highlight_col=None):
    rows_html = ""
    for _, row in df.iterrows():
        cells = ""
        for col in df.columns:
            val = row[col]
            style = ""
            if highlight_col and col == highlight_col:
                if "Normal" in str(val):
                    style = "color:#22D3EE;font-weight:700;"
                elif "Alerta" in str(val):
                    style = "color:#818CF8;font-weight:700;"
                elif "Anomalia" in str(val) or "Anomalía" in str(val):
                    style = "color:#A855F7;font-weight:700;"
            cells += f"<td style='padding:9px 14px;border-bottom:1px solid #1a1a40;color:#c8d0e8;font-size:0.85rem;{style}'>{val}</td>"
        rows_html += f"<tr style='transition:background 0.15s' onmouseover=\"this.style.background='#0D1340'\" onmouseout=\"this.style.background='transparent'\">{cells}</tr>"
    headers = "".join(
        f"<th style='padding:10px 14px;background:#0a0a22;color:#38BDF8;font-size:0.78rem;text-transform:uppercase;letter-spacing:1.2px;border-bottom:2px solid #818CF8;white-space:nowrap;'>{c}</th>"
        for c in df.columns
    )
    return f"""<div style='overflow-x:auto;border-radius:10px;border:1px solid #1a1a40;margin-top:6px'>
<table style='width:100%;border-collapse:collapse;background:#080818;font-family:Syne,sans-serif'>
<thead><tr>{headers}</tr></thead>
<tbody>{rows_html}</tbody>
</table></div>"""

# ─── CSS PERSONALIZADO ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

/* ── BASE ── */
html, body, [class*="css"], .stApp {
    font-family: 'Syne', sans-serif;
    background-color: #050510 !important;
    color: #e2e8f0 !important;
}
.main .block-container {
    background-color: #050510 !important;
    padding-top: 1.5rem;
    max-width: 1400px;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080818 0%, #0D1340 100%) !important;
    border-right: 1px solid #1a1a40;
}
[data-testid="stSidebar"] * { color: #a8b2d8 !important; }
[data-testid="stSidebar"] h3 { color: #e2e8f0 !important; font-weight: 800; }
[data-testid="stSidebar"] .stMarkdown { color: #8892b0 !important; }

/* ── WIDGETS SIDEBAR ── */
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-baseweb="input"],
[data-testid="stSidebar"] [data-baseweb="popover"] {
    background-color: #0a0a22 !important;
    border-color: #1a1a50 !important;
    color: #e2e8f0 !important;
}
[data-baseweb="select"] > div,
[data-baseweb="input"] {
    background-color: #0a0a22 !important;
    border-color: #1a1a50 !important;
    color: #e2e8f0 !important;
}
[data-baseweb="menu"] { background-color: #0B0B20 !important; }
[data-baseweb="option"] { background-color: #0B0B20 !important; color: #e2e8f0 !important; }
[data-baseweb="option"]:hover { background-color: #0D1340 !important; }
[data-baseweb="tag"] {
    background-color: #818CF8 !important;
    color: #fff !important;
}

/* Slider */
[data-testid="stSlider"] > div > div > div > div {
    background: #818CF8 !important;
}

/* ── TABS ── */
[data-baseweb="tab-list"] {
    background-color: #0a0a22 !important;
    border-radius: 10px 10px 0 0;
    gap: 4px;
    padding: 4px 6px 0 6px;
    border-bottom: 2px solid #1a1a40;
}
[data-baseweb="tab"] {
    background-color: #0B0B20 !important;
    color: #8892b0 !important;
    border-radius: 8px 8px 0 0 !important;
    font-weight: 600;
    font-size: 0.85rem;
    letter-spacing: 0.5px;
    padding: 10px 22px !important;
    border: 1px solid #1a1a40 !important;
    border-bottom: none !important;
    transition: all 0.2s;
}
[data-baseweb="tab"]:hover {
    background-color: #0D1340 !important;
    color: #e2e8f0 !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    background: linear-gradient(135deg, #0D1340 0%, #1a0a4a 100%) !important;
    color: #818CF8 !important;
    border-color: #818CF8 !important;
    border-bottom: 2px solid #050510 !important;
}
[data-baseweb="tab-panel"] {
    background-color: #080818 !important;
    border: 1px solid #1a1a40;
    border-top: none;
    border-radius: 0 0 10px 10px;
    padding: 18px 14px !important;
}

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] > div,
[data-testid="stDataFrame"] iframe,
.stDataFrame {
    background-color: #080818 !important;
    border: 1px solid #1a1a40 !important;
    border-radius: 10px !important;
}
.dvn-scroller { background-color: #080818 !important; }
.stDataFrame [data-testid="glideDataEditor"] {
    background: #080818 !important;
}

/* ── EXPANDER ── */
[data-testid="stExpander"] {
    background: linear-gradient(135deg, #08081a 0%, #0a0a22 100%) !important;
    border: 1px solid rgba(129,140,248,0.35) !important;
    border-radius: 16px !important;
    margin: 16px 0 !important;
    box-shadow: 0 4px 28px rgba(0,0,0,0.45),
                inset 0 1px 0 rgba(255,255,255,0.04) !important;
    transition: box-shadow 0.3s, border-color 0.3s !important;
    overflow: hidden !important;
}
[data-testid="stExpander"]:hover {
    border-color: rgba(129,140,248,0.65) !important;
    box-shadow: 0 8px 40px rgba(129,140,248,0.2),
                0 2px 12px rgba(0,0,0,0.45) !important;
}
[data-testid="stExpander"] summary {
    background: linear-gradient(90deg,
        rgba(129,140,248,0.16) 0%,
        rgba(56,189,248,0.07) 55%,
        transparent 100%) !important;
    color: #e2e8f0 !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 1.05rem !important;
    font-weight: 800 !important;
    letter-spacing: 2.5px !important;
    text-transform: uppercase !important;
    padding: 17px 24px !important;
    border-left: 4px solid #818CF8 !important;
    cursor: pointer !important;
    transition: background 0.25s, color 0.25s !important;
    list-style: none !important;
}
[data-testid="stExpander"] summary:hover {
    background: linear-gradient(90deg,
        rgba(129,140,248,0.26) 0%,
        rgba(56,189,248,0.12) 60%,
        transparent 100%) !important;
    color: #ffffff !important;
}
[data-testid="stExpander"] summary::-webkit-details-marker { display: none !important; }
[data-testid="stExpander"] summary svg {
    fill: #818CF8 !important;
    opacity: 0.9;
    width: 18px !important;
    height: 18px !important;
}
[data-testid="stExpander"] .streamlit-expanderContent,
[data-testid="stExpander"] details > div {
    background: transparent !important;
    padding: 20px 24px 18px 24px !important;
    border-top: 1px solid rgba(129,140,248,0.13) !important;
}

/* ── METRIC CARD (sección atípicos) ── */
.metric-card {
    background: linear-gradient(135deg, #0a0a22 0%, #0D1340 100%);
    border: 1px solid rgba(129,140,248,0.25);
    border-radius: 12px;
    padding: 18px 16px 14px 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.35);
    transition: transform 0.2s, box-shadow 0.2s;
    margin-bottom: 8px;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(129,140,248,0.2);
}

/* ── SELECTBOX PRINCIPAL ── */
[data-testid="stSelectbox"] label { color: #8892b0 !important; font-size: 0.82rem; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #050510; }
::-webkit-scrollbar-thumb { background: #1a1a50; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #818CF8; }

/* ── DIVIDER ── */
hr { border-color: #1a1a40 !important; }

/* ════════════ COMPONENTES PROPIOS ════════════ */

/* KPI cards */
.kpi-card {
    background: linear-gradient(135deg, #0a0a22 0%, #0D1340 100%);
    border: 1px solid rgba(129,140,248,0.4);
    border-radius: 14px;
    padding: 22px 24px 18px 24px;
    text-align: center;
    box-shadow: 0 6px 30px rgba(129,140,248,0.12), inset 0 1px 0 rgba(255,255,255,0.04);
    transition: transform 0.2s, box-shadow 0.2s;
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 40px rgba(129,140,248,0.22);
}
.kpi-icon  { font-size: 1.4rem; margin-bottom: 6px; }
.kpi-number {
    font-family: 'Space Mono', monospace;
    font-size: 2.6rem;
    font-weight: 700;
    color: #818CF8;
    line-height: 1;
    text-shadow: 0 0 20px rgba(129,140,248,0.5);
}
.kpi-label {
    font-size: 0.78rem;
    color: #8892b0;
    text-transform: uppercase;
    letter-spacing: 1.8px;
    margin-top: 7px;
}
.kpi-sub {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: #38BDF8;
    margin-top: 5px;
    opacity: 0.9;
}

/* Section headers */
.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 1.2rem;
    font-weight: 800;
    color: #e2e8f0;
    border-left: 4px solid #818CF8;
    padding: 8px 0 8px 16px;
    margin: 32px 0 18px 0;
    text-transform: uppercase;
    letter-spacing: 2px;
    background: linear-gradient(90deg, rgba(129,140,248,0.08) 0%, transparent 60%);
    border-radius: 0 8px 8px 0;
}

/* Hipótesis boxes */
.hipotesis-box {
    background: linear-gradient(135deg, #0a0a22 0%, #0d0d35 100%);
    border: 1px solid #1a1a50;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 14px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    transition: border-color 0.2s;
}
.hipotesis-box:hover { border-color: #818CF8; }
.h-title { font-weight: 700; color: #38BDF8; font-size: 0.95rem; margin-bottom: 10px; letter-spacing: 0.3px; }
.h-row   { display: flex; justify-content: space-between; margin: 5px 0; font-size: 0.84rem; color: #8892b0; border-bottom: 1px solid rgba(26,26,64,0.7); padding-bottom: 4px; }
.h-val   { font-family: 'Space Mono', monospace; color: #c8d0e8; font-size: 0.83rem; }
.rechaza    { color: #A855F7 !important; font-weight: 700; font-size: 0.88rem; }
.no-rechaza { color: #22D3EE !important; font-weight: 700; font-size: 0.88rem; }

/* Badges */
.badge-normal   { background:#22D3EE; color:#000; padding:3px 12px; border-radius:20px; font-size:0.75rem; font-weight:700; }
.badge-alerta   { background:#818CF8; color:#fff; padding:3px 12px; border-radius:20px; font-size:0.75rem; font-weight:700; }
.badge-anomalia { background:#A855F7; color:#fff; padding:3px 12px; border-radius:20px; font-size:0.75rem; font-weight:700; }
</style>
""", unsafe_allow_html=True)

# ─── CARGA DE DATOS ───────────────────────────────────────────────────────────
@st.cache_data
def cargar_datos():
    df = pd.read_excel("CALCULOS TRABAJO ESTADISTICA.xlsx")
    df = df[df["Tipo_Evento"].isin(["Normal", "Alerta", "Anomalia"])].copy()
    df.columns = [
        "ID", "Monto", "Tiempo", "Frecuencia", "Score",
        "Tipo_Evento", "Ubicacion", "Dispositivo",
        "Estado_Cuenta", "Resultado_Modelo", "Resultado_Hipotesis"
    ]
    for c in ["Monto", "Tiempo", "Frecuencia", "Score"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

try:
    df = cargar_datos()
    datos_ok = True
except Exception as e:
    datos_ok = False
    st.error(f"No se pudo cargar el archivo Excel: {e}")
    st.info("Asegúrate de que **CALCULOS_TRABAJO_ESTADISTICA.xlsx** esté en la misma carpeta que app.py")
    st.stop()

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 Filtros")
    tipos_sel = st.multiselect(
        "Tipo de Evento",
        options=["Normal", "Alerta", "Anomalia"],
        default=["Normal", "Alerta", "Anomalia"]
    )
    ubicaciones_sel = st.multiselect(
        "Ubicación",
        options=sorted(df["Ubicacion"].unique()),
        default=sorted(df["Ubicacion"].unique())
    )
    dispositivos_sel = st.multiselect(
        "Dispositivo",
        options=sorted(df["Dispositivo"].unique()),
        default=sorted(df["Dispositivo"].unique())
    )
    score_range = st.slider("Rango Score Anomalía", 0.0, 1.0, (0.0, 1.0), 0.01)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.75rem;color:#8892b0;line-height:1.6'>
    📘 <b style='color:#38BDF8'>Trabajo</b><br>
    Detección de Anomalías en Sistemas<br><br>
    📊 <b style='color:#38BDF8'>Estadística Inferencial</b><br>
    Pruebas de hipótesis con confianza &gt; 90%<br><br>
    🗄️ <b style='color:#38BDF8'>Base de datos</b><br>
    500 transacciones digitales
    </div>
    """, unsafe_allow_html=True)

# ─── FILTRAR ──────────────────────────────────────────────────────────────────
df_f = df[
    df["Tipo_Evento"].isin(tipos_sel) &
    df["Ubicacion"].isin(ubicaciones_sel) &
    df["Dispositivo"].isin(dispositivos_sel) &
    df["Score"].between(score_range[0], score_range[1])
]

# ─── TÍTULO ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding: 18px 0 10px 0; border-bottom: 1px solid #1e2a4a; margin-bottom: 8px;'>
  <div style='font-family:Space Mono,monospace;font-size:0.72rem;color:#818CF8;letter-spacing:5px;margin-bottom:8px;opacity:0.8'>
    ◈ ANÁLISIS ESTADÍSTICO ◈
  </div>
  <div style='font-family:Syne,sans-serif;font-size:1.8rem;font-weight:800;color:#e2e8f0;letter-spacing:1px;line-height:1.3;text-shadow:0 0 40px rgba(129,140,248,0.3)'>
    ANÁLISIS ESTADÍSTICO DESCRIPTIVO E INFERENCIAL PARA LA IDENTIFICACIÓN DE COMPORTAMIENTOS ANÓMALOS EN TRANSACCIONES DIGITALES
  </div>
  <div style='margin-top:12px;display:flex;justify-content:center;gap:8px'>
   
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 0 — KPIs
# ═══════════════════════════════════════════════════════════════════════════════
total      = len(df_f)
anomalias  = len(df_f[df_f["Tipo_Evento"] == "Anomalia"])
alertas    = len(df_f[df_f["Tipo_Evento"] == "Alerta"])
rechaza    = len(df_f[df_f["Resultado_Hipotesis"] == "Rechaza H0"])
pct_anom   = (anomalias / total * 100) if total else 0
pct_alerta = (alertas / total * 100) if total else 0
pct_rech   = (rechaza / total * 100) if total else 0

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class='kpi-card'>
        <div class='kpi-icon'>🗄️</div>
        <div class='kpi-number'>{total}</div>
        <div class='kpi-label'>Transacciones</div>
        <div class='kpi-sub'>Incluidad en la BD</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class='kpi-card'>
        <div class='kpi-icon'>🚨</div>
        <div class='kpi-number'>{anomalias}</div>
        <div class='kpi-label'>Anomalías Detectadas</div>
        <div class='kpi-sub'>{pct_anom:.1f}% del total</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class='kpi-card'>
        <div class='kpi-icon'>⚠️</div>
        <div class='kpi-number'>{alertas}</div>
        <div class='kpi-label'>Alertas</div>
        <div class='kpi-sub'>{pct_alerta:.1f}% del total</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class='kpi-card'>
        <div class='kpi-icon'>📊</div>
        <div class='kpi-number'>{rechaza}</div>
        <div class='kpi-label'>Rechaza H₀</div>
        <div class='kpi-sub'>{pct_rech:.1f}% de pruebas</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 1 — IDENTIFICACIÓN DE VARIABLES
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("① Identificación de Variables", expanded=True):

    variables_info = {
        "Variable": ["Monto_Transaccion", "Tiempo_Entre_Transacciones", "Frecuencia_Por_Hora",
                     "Score_Anomalia", "Frecuencia_Por_Hora*", "Tipo_Evento",
                     "Ubicacion", "Dispositivo", "Estado_Cuenta", "Resultado_Modelo", "Resultado_Hipotesis"],
        "Tipo": ["Cuantitativa Continua", "Cuantitativa Continua", "Cuantitativa Discreta", "Cuantitativa Continua", "Cuantitativa Discreta",
                 "Cualitativa Nominal", "Cualitativa Nominal", "Cualitativa Nominal",
                 "Cualitativa Nominal", "Binaria (0/1)", "Cualitativa Nominal"],
        "Unidad / Categorías": [
            "$COP", "Segundos", "0 – 8 transacciones/hora", "0 a 1 (probabilidad)",
            "Valores enteros", "Tres tipos: Normal · Alerta · Anomalía",
            "Bogotá · Medellín · Cali · Barranquilla", "Móvil · API · Escritorio",
            "Activa · Bloqueada · Suspendida", "0 = No anomalía / 1 = Anomalía",
            "Rechaza H₀ · No rechaza H₀"
        ],
        "Rol en el análisis": [
            "Variable de estudio principal", "Indicador de comportamiento temporal",
            "Indicador de actividad", "Variable simulada de riesgo asociada a cada transacción.",
            "Variable cuantitativa discreta", "Permite segmentar los datos y comparar estadísticamente el comportamiento de las demás variables entre grupos",
            "Variable de contexto geográfico", "Canal de acceso",
            "Estado del usuario", "Salida del modelo de detección",
            "Resultado de la prueba estadística"
        ]
    }

    df_vars = pd.DataFrame(variables_info).drop_duplicates(subset="Variable")
    st.markdown(df_to_html(df_vars, highlight_col="Variable"), unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 2 — ESTADÍSTICAS DESCRIPTIVAS
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("② Estadísticas Descriptivas", expanded=True):

    tab_tabla, tab_hist, tab_box = st.tabs(["📋 Tabla resumen", "📊 Histogramas", "📦 Boxplots"])

    vars_num = {
        "Monto ($COP)": "Monto",
        "Tiempo entre trans. (s)": "Tiempo",
        "Frecuencia / hora": "Frecuencia",
        "Score Anomalía": "Score"
    }

    with tab_tabla:
        resumen_rows = []
        for label, col in vars_num.items():
            s = df_f[col].dropna()
            q1, q3 = s.quantile(0.25), s.quantile(0.75)
            resumen_rows.append({
                "Variable": label,
                "Media": f"{s.mean():,.2f}",
                "Mediana": f"{s.median():,.2f}",
                "Desv. Est.": f"{s.std():,.2f}",
                "Mínimo": f"{s.min():,.2f}",
                "Máximo": f"{s.max():,.2f}",
                "Q1 (25%)": f"{q1:,.2f}",
                "Q3 (75%)": f"{q3:,.2f}",
                "Rango IQR": f"{q3-q1:,.2f}"
            })
        st.markdown(df_to_html(pd.DataFrame(resumen_rows)), unsafe_allow_html=True)

    with tab_hist:
        fig_hist = make_subplots(rows=2, cols=2, subplot_titles=list(vars_num.keys()))
        positions = [(1,1),(1,2),(2,1),(2,2)]
        for (label, col), (r, c) in zip(vars_num.items(), positions):
            for tipo in ["Normal", "Alerta", "Anomalia"]:
                sub = df_f[df_f["Tipo_Evento"] == tipo][col].dropna()
                fig_hist.add_trace(
                    go.Histogram(x=sub, name=tipo, marker_color=TIPO_COLORS[tipo],
                                 opacity=0.7, showlegend=(r==1 and c==1)),
                    row=r, col=c
                )
        fig_hist.update_layout(
            barmode="overlay", height=500,
            paper_bgcolor="#0a0a1a", plot_bgcolor="#0a0a1a",
            font_color="#a8b2d8", title_text="Distribución por tipo de evento",
            legend=dict(bgcolor="#0B0B20", bordercolor="#818CF8", borderwidth=1)
        )
        fig_hist.update_xaxes(gridcolor="#16213E")
        fig_hist.update_yaxes(gridcolor="#16213E")
        st.plotly_chart(fig_hist, use_container_width=True)

    with tab_box:
        col_sel = st.selectbox("Variable para boxplot", list(vars_num.keys()))
        col_real = vars_num[col_sel]
        fig_box = px.box(
            df_f, x="Tipo_Evento", y=col_real,
            color="Tipo_Evento",
            color_discrete_map=TIPO_COLORS,
            points="outliers",
            title=f"Distribución de {col_sel} por Tipo de Evento"
        )
        fig_box.update_layout(
            paper_bgcolor="#0a0a1a", plot_bgcolor="#0a0a1a",
            font_color="#a8b2d8", height=420,
            legend_title_text="Tipo Evento",
            legend=dict(bgcolor="#0B0B20", bordercolor="#818CF8")
        )
        fig_box.update_xaxes(gridcolor="#16213E")
        fig_box.update_yaxes(gridcolor="#16213E")
        st.plotly_chart(fig_box, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 3 — TABLAS DE FRECUENCIA
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("③ Tablas de Frecuencia", expanded=True):

    col_f1, col_f2 = st.columns(2)

    vars_cat = {
        "Tipo de Evento": "Tipo_Evento",
        "Ubicación": "Ubicacion",
        "Dispositivo": "Dispositivo",
        "Estado de Cuenta": "Estado_Cuenta"
    }

    cat_list = list(vars_cat.items())
    pairs = [(cat_list[0], cat_list[1]), (cat_list[2], cat_list[3])]

    for (la, ca), (lb, cb) in pairs:
        col_l, col_r = st.columns(2)
        with col_l:
            freq = df_f[ca].value_counts().reset_index()
            freq.columns = [la, "Frecuencia"]
            freq["Porcentaje"] = (freq["Frecuencia"] / freq["Frecuencia"].sum() * 100).round(1)
            freq["% txt"] = freq["Porcentaje"].astype(str) + "%"
            color_map = TIPO_COLORS if ca == "Tipo_Evento" else None
            fig_pie = px.pie(
                freq, names=la, values="Frecuencia",
                title=f"Distribución: {la}",
                color=la if ca == "Tipo_Evento" else None,
                color_discrete_map=color_map if color_map else px.colors.qualitative.Set2
            )
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            fig_pie.update_layout(
                paper_bgcolor="#0a0a1a", font_color="#a8b2d8",
                height=320, showlegend=False,
                margin=dict(t=40, b=10, l=10, r=10)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown(df_to_html(freq[[la, "Frecuencia", "% txt"]].rename(columns={"% txt": "%"})), unsafe_allow_html=True)

        with col_r:
            freq2 = df_f[cb].value_counts().reset_index()
            freq2.columns = [lb, "Frecuencia"]
            freq2["Porcentaje"] = (freq2["Frecuencia"] / freq2["Frecuencia"].sum() * 100).round(1)
            freq2["% txt"] = freq2["Porcentaje"].astype(str) + "%"
            fig_bar = px.bar(
                freq2, x=lb, y="Frecuencia",
                title=f"Distribución: {lb}",
                color="Frecuencia",
                color_continuous_scale=["#1E3A8A", "#A855F7"]
            )
            fig_bar.update_layout(
                paper_bgcolor="#0a0a1a", plot_bgcolor="#0a0a1a",
                font_color="#a8b2d8", height=320, coloraxis_showscale=False,
                margin=dict(t=40, b=10, l=10, r=10)
            )
            fig_bar.update_xaxes(gridcolor="#16213E")
            fig_bar.update_yaxes(gridcolor="#16213E")
            st.plotly_chart(fig_bar, use_container_width=True)
            st.markdown(df_to_html(freq2[[lb, "Frecuencia", "% txt"]].rename(columns={"% txt": "%"})), unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 4 — DETECCIÓN DE ANOMALÍAS
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("④ Detección de Valores Atípicos — Métodos IQR y Regla 3σ", expanded=True):

    @st.cache_data
    def cargar_atipicos():
        resumen = pd.read_excel(
            "CALCULOS TRABAJO ESTADISTICA.xlsx",
            sheet_name="DETECCION_ATIPICOS", header=3, nrows=4
        )
        resumen.columns = ["Variable", "Q1", "Q3", "IQR", "Lim_Inf_IQR", "Lim_Sup_IQR",
                           "N_Atip_IQR", "N_Atip_3sigma", "Pct_IQR"]
        registros = pd.read_excel(
            "CALCULOS TRABAJO ESTADISTICA.xlsx",
            sheet_name="DETECCION_ATIPICOS", header=10, nrows=23
        )
        registros.columns = ["ID", "Monto", "Tipo_Evento", "Ubicacion", "Dispositivo",
                             "Score", "Es_Anomalia", "Pos_Q3", "Nota"]
        return resumen, registros

    df_res_at, df_reg_at = cargar_atipicos()

    # ── KPI cards ─────────────────────────────────────────────────────────────────
    at_kpi_cols = st.columns(4)
    kpi_at_data = [
        ("Atípicos IQR\nMonto", "23", "4.6 % del total", "#38BDF8"),
        ("Atípicos IQR\nTiempo", "26", "5.2 % del total", "#818CF8"),
        ("Atípicos 3σ\nMonto + Tiempo", "17", "Monto: 9  ·  Tiempo: 8", "#A855F7"),
        ("Sin Atípicos\nFrecuencia y Score", "0", "IQR y 3σ = 0", "#22D3EE"),
    ]
    for col, (titulo, valor, sub, color) in zip(at_kpi_cols, kpi_at_data):
        with col:
            st.markdown(f"""
            <div class='metric-card' style='border-left:3px solid {color};text-align:center'>
              <div style='font-family:Space Mono,monospace;font-size:0.65rem;color:#8892b0;
                          letter-spacing:2px;text-transform:uppercase;margin-bottom:6px;white-space:pre-line'>{titulo}</div>
              <div style='font-size:1.9rem;font-weight:700;color:{color};font-family:Space Mono,monospace'>{valor}</div>
              <div style='font-size:0.72rem;color:#64748b;margin-top:4px'>{sub}</div>
            </div>""", unsafe_allow_html=True)

    # ── Tabla resumen IQR ─────────────────────────────────────────────────────────
    st.markdown("""<div style='margin:18px 0 6px 0;font-family:Space Mono,monospace;font-size:0.72rem;
    color:#818CF8;letter-spacing:3px;text-transform:uppercase'>Resumen de Valores Atípicos por Variable</div>""",
    unsafe_allow_html=True)

    tabla_at = df_res_at.copy()
    for c in ["Q1", "Q3", "IQR", "Lim_Inf_IQR", "Lim_Sup_IQR"]:
        tabla_at[c] = pd.to_numeric(tabla_at[c], errors="coerce").round(4)
    tabla_at["N_Atip_IQR"]    = pd.to_numeric(tabla_at["N_Atip_IQR"],    errors="coerce").fillna(0).astype(int)
    tabla_at["N_Atip_3sigma"] = pd.to_numeric(tabla_at["N_Atip_3sigma"], errors="coerce").fillna(0).astype(int)
    tabla_at["Pct_IQR"]       = pd.to_numeric(tabla_at["Pct_IQR"],       errors="coerce").fillna(0)
    tabla_at_display = tabla_at.rename(columns={
        "Lim_Inf_IQR": "Lím. Inf. (IQR)", "Lim_Sup_IQR": "Lím. Sup. (IQR)",
        "N_Atip_IQR": "# Atíp. IQR", "N_Atip_3sigma": "# Atíp. 3σ", "Pct_IQR": "% Atíp. IQR"
    })
    st.markdown(df_to_html(tabla_at_display), unsafe_allow_html=True)

    # ── Gráfico barras agrupadas + Scatter atípicos ───────────────────────────────
    d4c1, d4c2 = st.columns([1, 1])

    with d4c1:
        variables_bar = df_res_at["Variable"].tolist()
        iqr_vals   = pd.to_numeric(df_res_at["N_Atip_IQR"],    errors="coerce").fillna(0).tolist()
        sigma_vals = pd.to_numeric(df_res_at["N_Atip_3sigma"], errors="coerce").fillna(0).tolist()
        fig_at_bar = go.Figure()
        fig_at_bar.add_trace(go.Bar(
            name="IQR", x=variables_bar, y=iqr_vals,
            marker_color="#38BDF8", text=iqr_vals, textposition="outside"
        ))
        fig_at_bar.add_trace(go.Bar(
            name="Regla 3σ", x=variables_bar, y=sigma_vals,
            marker_color="#A855F7", text=sigma_vals, textposition="outside"
        ))
        fig_at_bar.update_layout(
            title="# Atípicos por Variable y Método",
            barmode="group",
            paper_bgcolor="#0a0a1a", plot_bgcolor="#0a0a1a",
            font_color="#a8b2d8", height=350,
            legend=dict(bgcolor="#0B0B20", bordercolor="#818CF8"),
            yaxis_range=[0, 32]
        )
        fig_at_bar.update_xaxes(gridcolor="#16213E", tickangle=-15)
        fig_at_bar.update_yaxes(gridcolor="#16213E")
        st.plotly_chart(fig_at_bar, use_container_width=True)

    with d4c2:
        df_reg_plot = df_reg_at.copy()
        df_reg_plot["Monto"] = pd.to_numeric(df_reg_plot["Monto"], errors="coerce")
        df_reg_plot["Score"] = pd.to_numeric(df_reg_plot["Score"], errors="coerce")
        fig_scatter = px.scatter(
            df_reg_plot, x="Monto", y="Score",
            color="Tipo_Evento", color_discrete_map=TIPO_COLORS,
            title="Registros Atípicos: Monto vs Score",
            opacity=0.85, size_max=10,
            hover_data=["ID", "Ubicacion", "Dispositivo", "Nota"]
        )
        fig_scatter.update_layout(
            paper_bgcolor="#0a0a1a", plot_bgcolor="#0a0a1a",
            font_color="#a8b2d8", height=350,
            legend=dict(bgcolor="#0B0B20", bordercolor="#818CF8")
        )
        fig_scatter.update_xaxes(gridcolor="#16213E")
        fig_scatter.update_yaxes(gridcolor="#16213E")
        st.plotly_chart(fig_scatter, use_container_width=True)

    # ── Tabla de registros atípicos ───────────────────────────────────────────────
    st.markdown("""<div style='margin:10px 0 6px 0;font-family:Space Mono,monospace;font-size:0.72rem;
    color:#818CF8;letter-spacing:3px;text-transform:uppercase'>Registros Atípicos — Monto_Transaccion (Método IQR)</div>""",
    unsafe_allow_html=True)
    tabla_reg = df_reg_at[["ID", "Monto", "Tipo_Evento", "Ubicacion", "Dispositivo",
                            "Score", "Es_Anomalia", "Pos_Q3", "Nota"]].copy()
    tabla_reg["Monto"] = pd.to_numeric(tabla_reg["Monto"], errors="coerce").round(2)
    tabla_reg["Score"] = pd.to_numeric(tabla_reg["Score"], errors="coerce").round(4)
    st.markdown(df_to_html(tabla_reg, highlight_col="Tipo_Evento"), unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 5B — CÁLCULOS DETALLADOS HOJA "PRUEBA DE HIPOTESIS"
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("⑤ PRUEBAS DE HIPOTESIS", expanded=True):



    # ── Datos fijos leídos de la hoja Excel ──────────────────────────────────────
    datos_p1 = {
        "Media Normal":       0.2267,
        "Media Anomalía":     0.6609,
        "Desviación Normal":  0.0972,
        "Desviación Anomalía":0.0614,
        "n Normal":           366,
        "n Anomalía":         19,
        "Estadístico t":     -28.9961,
        "P-Valor":            1.37e-19,
    }
    datos_p2 = {
        "Media Normal":       26221.91,
        "Media Anomalía":     25342.48,
        "Desviación Normal":  10431.62,
        "Desviación Anomalía":11052.47,
        "n Normal":           366,
        "n Anomalía":         19,
        "Estadístico t":      0.33908,
        "P-Valor":            0.7717,
    }

    def render_prueba_excel(titulo, variable, tipo_prueba, h0, h1, datos, rechaza, conclusion):
        color_resultado = "#A855F7" if rechaza else "#22D3EE"
        icono_resultado = "✗ RECHAZA H₀" if rechaza else "✓ NO RECHAZA H₀"
        # Construir filas de datos
        filas = ""
        for k, v in datos.items():
            if isinstance(v, float):
                if abs(v) < 0.0001:
                    val_str = f"{v:.2e}"
                else:
                    val_str = f"{v:,.4f}"
            else:
                val_str = str(v)
            filas += f"""<div style='display:flex;justify-content:space-between;padding:7px 0;
                border-bottom:1px solid rgba(26,26,64,0.6);font-size:0.84rem'>
                <span style='color:#8892b0'>{k}</span>
                <span style='font-family:Space Mono,monospace;color:#c8d0e8'>{val_str}</span>
            </div>"""

        return f"""
        <div style='background:linear-gradient(135deg,#0a0a22 0%,#0d0d35 100%);
                    border:1px solid #1a1a50;border-radius:14px;padding:22px 26px;
                    box-shadow:0 4px 24px rgba(0,0,0,0.4);transition:border-color 0.2s'
             onmouseover="this.style.borderColor='#818CF8'" onmouseout="this.style.borderColor='#1a1a50'">

          <!-- Header -->
          <div style='font-family:Space Mono,monospace;font-size:0.7rem;color:#818CF8;
                      letter-spacing:3px;margin-bottom:6px;text-transform:uppercase'>{tipo_prueba}</div>
          <div style='font-weight:800;color:#e2e8f0;font-size:1rem;margin-bottom:4px'>{titulo}</div>
          <div style='font-size:0.78rem;color:#38BDF8;margin-bottom:16px'>Variable: <b>{variable}</b></div>

          <!-- Hipótesis -->
          <div style='background:#050510;border-radius:8px;padding:12px 16px;margin-bottom:14px'>
            <div style='font-size:0.78rem;color:#818CF8;font-weight:700;letter-spacing:1px;
                        margin-bottom:8px;text-transform:uppercase'>Hipótesis</div>
            <div style='display:flex;gap:8px;margin-bottom:6px;font-size:0.84rem'>
              <span style='background:rgba(56,189,248,0.15);color:#38BDF8;padding:2px 10px;
                           border-radius:4px;font-weight:700;white-space:nowrap'>H₀</span>
              <span style='color:#c8d0e8'>{h0}</span>
            </div>
            <div style='display:flex;gap:8px;font-size:0.84rem'>
              <span style='background:rgba(168,85,247,0.15);color:#A855F7;padding:2px 10px;
                           border-radius:4px;font-weight:700;white-space:nowrap'>H₁</span>
              <span style='color:#c8d0e8'>{h1}</span>
            </div>
          </div>

          <!-- Parámetros -->
          <div style='display:flex;gap:10px;margin-bottom:14px'>
            <div style='flex:1;background:#050510;border-radius:8px;padding:10px 14px;text-align:center'>
              <div style='font-size:0.7rem;color:#8892b0;letter-spacing:1px;text-transform:uppercase'>Significancia</div>
              <div style='font-family:Space Mono,monospace;font-size:1.1rem;color:#818CF8;font-weight:700'>α = 0.05</div>
            </div>
            <div style='flex:1;background:#050510;border-radius:8px;padding:10px 14px;text-align:center'>
              <div style='font-size:0.7rem;color:#8892b0;letter-spacing:1px;text-transform:uppercase'>Confianza</div>
              <div style='font-family:Space Mono,monospace;font-size:1.1rem;color:#22D3EE;font-weight:700'>95%</div>
            </div>
          </div>

          <!-- Datos calculados -->
          <div style='background:#050510;border-radius:8px;padding:12px 16px;margin-bottom:14px'>
            <div style='font-size:0.78rem;color:#818CF8;font-weight:700;letter-spacing:1px;
                        margin-bottom:10px;text-transform:uppercase'>Datos & Resultados</div>
            {filas}
          </div>

          <!-- Resultado -->
          <div style='background:rgba({("168,85,247" if rechaza else "34,211,238")},0.12);
                      border:1px solid {color_resultado};border-radius:8px;
                      padding:10px 16px;text-align:center;margin-bottom:12px'>
            <span style='font-family:Space Mono,monospace;font-weight:700;color:{color_resultado};
                         font-size:0.95rem'>{icono_resultado}</span>
            <span style='color:#8892b0;font-size:0.8rem;margin-left:10px'>
              p = {datos["P-Valor"]:.2e} {"&lt;" if rechaza else "≥"} 0.05
            </span>
          </div>

          <!-- Conclusión -->
          <div style='font-size:0.82rem;color:#a8b2d8;line-height:1.7;
                      border-top:1px solid #1a1a40;padding-top:12px'>
            <b style='color:#38BDF8'>Conclusión:</b> {conclusion}
          </div>
        </div>
        """

    col_ep1, col_ep2 = st.columns(2)

    with col_ep1:
        st.markdown(render_prueba_excel(
            titulo    = "t de Student: Score_Anomalia",
            variable  = "Score_Anomalia",
            tipo_prueba = "PRUEBA 1 — Unilateral (cola derecha)",
            h0        = "μ(Score_Normal) = μ(Score_Anomalía)",
            h1        = "μ(Score_Anomalía) > μ(Score_Normal)",
            datos     = datos_p1,
            rechaza   = True,
            conclusion= "Obteniendo un p-valor inferior al nivel de significancia establecido (0.05), "
                        "se rechazó la hipótesis nula y se concluyó que los comportamientos atípicos "
                        "presentan características <b style='color:#A855F7'>significativamente diferentes</b> "
                        "respecto al comportamiento normal de la población analizada."
        ), unsafe_allow_html=True)

    with col_ep2:
        st.markdown(render_prueba_excel(
            titulo    = "t de Student: Monto_Transaccion",
            variable  = "Monto_Transaccion",
            tipo_prueba = "PRUEBA 2 — Bilateral",
            h0        = "μ(Monto_Normal) = μ(Monto_Anomalía)",
            h1        = "μ(Monto_Normal) ≠ μ(Monto_Anomalía)",
            datos     = datos_p2,
            rechaza   = False,
            conclusion= "El p-valor fue de 0.7717, superior al nivel de significancia de 0.05. "
                        "Por lo tanto, <b style='color:#22D3EE'>no se rechazó la hipótesis nula</b>, "
                        "concluyendo que no existen diferencias estadísticamente significativas entre "
                        "los montos promedio de las transacciones normales y las transacciones atípicas."
        ), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 6 — INTERVALOS DE CONFIANZA
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("⑥ Intervalos de Confianza (95%)", expanded=True):

    # ── Cargar datos directamente desde Hoja2 ────────────────────────────────────
    @st.cache_data
    def cargar_intervalos():
        df_ic_raw = pd.read_excel(
            "CALCULOS TRABAJO ESTADISTICA.xlsx",
            sheet_name="Hoja2", header=2
        )
        df_ic_raw.columns = [
            "Variable", "Grupo", "n", "Media", "Desv_Est", "Error_Est",
            "IC95_Inf", "IC95_Sup", "IC99_Inf", "IC99_Sup", "Distribucion"
        ]
        df_ic_raw = df_ic_raw.dropna(subset=["Variable", "Grupo"])
        for c in ["n", "Media", "Desv_Est", "Error_Est", "IC95_Inf", "IC95_Sup", "IC99_Inf", "IC99_Sup"]:
            df_ic_raw[c] = pd.to_numeric(df_ic_raw[c], errors="coerce")
        return df_ic_raw

    df_ic_excel = cargar_intervalos()

    # ── Tabla resumen completa ────────────────────────────────────────────────────
    tabla_display = df_ic_excel[[
        "Variable", "Grupo", "n", "Media",
        "Desv_Est", "Error_Est",
        "IC95_Inf", "IC95_Sup",
        "IC99_Inf", "IC99_Sup", "Distribucion"
    ]].copy()
    tabla_display.columns = [
        "Variable", "Grupo", "n", "Media",
        "Desv. Est.", "Error Est.",
        "IC 95% Inf.", "IC 95% Sup.",
        "IC 99% Inf.", "IC 99% Sup.", "Distribución"
    ]
    for c in ["Media", "Desv. Est.", "Error Est.", "IC 95% Inf.", "IC 95% Sup.", "IC 99% Inf.", "IC 99% Sup."]:
        tabla_display[c] = tabla_display[c].apply(lambda x: f"{x:,.4f}" if pd.notna(x) else "")
    tabla_display["n"] = tabla_display["n"].apply(lambda x: int(x) if pd.notna(x) else "")

    st.markdown(df_to_html(tabla_display), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Gráficas por variable ─────────────────────────────────────────────────────
    variables_ic = df_ic_excel["Variable"].unique().tolist()
    var_sel = st.selectbox("Selecciona variable para visualizar intervalos:", variables_ic, key="ic_var")

    df_var = df_ic_excel[df_ic_excel["Variable"] == var_sel].copy()

    GRUPO_COLORS = {
        "Normal":   COLOR_NORMAL,
        "Alerta":   COLOR_ALERTA,
        "Anomalia": COLOR_ANOMALIA,
    }

    fig_ic = go.Figure()

    for _, row in df_var.iterrows():
        grupo  = row["Grupo"]
        media  = row["Media"]
        color  = GRUPO_COLORS.get(grupo, "#818CF8")
        y_pos  = grupo

        # Banda IC 99% (más ancha, translúcida)
        fig_ic.add_trace(go.Scatter(
            x=[row["IC99_Inf"], row["IC99_Sup"]],
            y=[y_pos, y_pos],
            mode="lines",
            line=dict(color=color, width=3, dash="dot"),
            opacity=0.45,
            name=f"{grupo} — IC 99%",
            showlegend=True,
            legendgroup=grupo + "_99"
        ))

        # Banda IC 95% (más estrecha, sólida)
        fig_ic.add_trace(go.Scatter(
            x=[row["IC95_Inf"], row["IC95_Sup"]],
            y=[y_pos, y_pos],
            mode="lines",
            line=dict(color=color, width=7),
            opacity=0.9,
            name=f"{grupo} — IC 95%",
            showlegend=True,
            legendgroup=grupo + "_95"
        ))

        # Punto de la media
        fig_ic.add_trace(go.Scatter(
            x=[media],
            y=[y_pos],
            mode="markers+text",
            marker=dict(color="white", size=13, line=dict(color=color, width=2.5)),
            text=[f"  {media:,.4f}"],
            textposition="middle right",
            textfont=dict(color="#e2e8f0", size=11, family="Space Mono"),
            name=f"{grupo} — Media",
            showlegend=False,
            legendgroup=grupo
        ))

    fig_ic.update_layout(
        title=f"Intervalos de Confianza 95% y 99% — {var_sel}",
        paper_bgcolor="#0a0a1a",
        plot_bgcolor="#0a0a1a",
        font_color="#a8b2d8",
        height=320,
        xaxis_title=var_sel,
        yaxis_title="Grupo",
        legend=dict(
            bgcolor="#0B0B20",
            bordercolor="#818CF8",
            borderwidth=1,
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="left",   x=0
        ),
        margin=dict(t=80, b=40, l=20, r=20)
    )
    fig_ic.update_xaxes(gridcolor="#16213E", zeroline=False)
    fig_ic.update_yaxes(gridcolor="#16213E")
    st.plotly_chart(fig_ic, use_container_width=True)

    # ── Tarjetas de detalle por grupo ─────────────────────────────────────────────
    cols_ic = st.columns(len(df_var))
    for col_ic, (_, row) in zip(cols_ic, df_var.iterrows()):
        grupo = row["Grupo"]
        color = GRUPO_COLORS.get(grupo, "#818CF8")
        amp95 = row["IC95_Sup"] - row["IC95_Inf"]
        amp99 = row["IC99_Sup"] - row["IC99_Inf"]
        with col_ic:
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#0a0a22 0%,#0d0d35 100%);
                        border:1px solid {color};border-radius:12px;padding:16px 18px;text-align:center'>
              <div style='font-family:Space Mono,monospace;font-size:0.7rem;color:{color};
                          letter-spacing:2px;text-transform:uppercase;margin-bottom:8px'>{grupo}</div>
              <div style='font-family:Space Mono,monospace;font-size:1.5rem;font-weight:700;
                          color:#e2e8f0;line-height:1'>{row["Media"]:,.4f}</div>
              <div style='font-size:0.7rem;color:#8892b0;margin:6px 0 12px 0;letter-spacing:1px'>MEDIA</div>
              <div style='background:#050510;border-radius:8px;padding:10px 12px;margin-bottom:8px'>
                <div style='font-size:0.7rem;color:#22D3EE;font-weight:700;letter-spacing:1px;margin-bottom:6px'>IC 95%</div>
                <div style='font-family:Space Mono,monospace;font-size:0.78rem;color:#c8d0e8'>
                  [{row["IC95_Inf"]:,.4f} — {row["IC95_Sup"]:,.4f}]
                </div>
                <div style='font-size:0.7rem;color:#8892b0;margin-top:4px'>Amplitud: {amp95:,.4f}</div>
              </div>
              <div style='background:#050510;border-radius:8px;padding:10px 12px'>
                <div style='font-size:0.7rem;color:#A855F7;font-weight:700;letter-spacing:1px;margin-bottom:6px'>IC 99%</div>
                <div style='font-family:Space Mono,monospace;font-size:0.78rem;color:#c8d0e8'>
                  [{row["IC99_Inf"]:,.4f} — {row["IC99_Sup"]:,.4f}]
                </div>
                <div style='font-size:0.7rem;color:#8892b0;margin-top:4px'>Amplitud: {amp99:,.4f}</div>
              </div>
              <div style='margin-top:10px;font-size:0.7rem;color:#8892b0'>
                n = <b style='color:#e2e8f0'>{int(row["n"])}</b> &nbsp;|&nbsp;
                Dist.: <b style='color:{color}'>{row["Distribucion"]}</b>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div style='background:#0B0B20;border-left:4px solid #38BDF8;padding:14px 18px;border-radius:0 8px 8px 0;margin-top:8px;font-size:0.86rem;color:#a8b2d8'>
    💡 <b style='color:#38BDF8'>Interpretación:</b> Los intervalos de confianza de los tres grupos
    <b>no se solapan</b>, lo que confirma estadísticamente que las diferencias entre Normal, Alerta
    y Anomalía son reales y no producto del azar. Esto valida que el Score_Anomalia discrimina
    correctamente los tipos de eventos con una confianza del 95%.
    </div>
    """, unsafe_allow_html=True)
