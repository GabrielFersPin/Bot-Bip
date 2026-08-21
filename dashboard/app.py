import os
import sys
from datetime import datetime, timedelta

# Asegurar que el directorio raíz esté en el PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from db.supabase_client import get_db_client

# ==============================================================================
# CONFIGURACIÓN DE LA PÁGINA Y ESTILOS DE STREAMLIT
# ==============================================================================

st.set_page_config(
    page_title="Bot-Bip | Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para diseño premium
st.markdown("""
    <style>
    /* Estilos generales */
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    /* Header estilizado */
    .dashboard-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    
    .dashboard-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    /* Tarjetas KPI */
    .kpi-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        transition: transform 0.2s ease-in-out;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: #38bdf8;
    }

    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #38bdf8;
    }

    .kpi-label {
        font-size: 0.9rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Tablas y gráficos */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def init_db():
    """Inicializa la conexión con Supabase mediante el helper de DB."""
    try:
        return get_db_client(use_service_role=False)
    except Exception as e:
        st.error(f"Error conectando a Supabase: {e}")
        return None


db = init_db()

# ==============================================================================
# ENCABEZADO Y BARRA LATERAL (FILTROS)
# ==============================================================================

st.markdown("""
<div class="dashboard-header">
    <h1 class="dashboard-title">📊 Bot-Bip Analytics & Dashboard</h1>
    <p style="color: #94a3b8; margin-top: 8px; margin-bottom: 0;">
        Plataforma analítica de seguimiento diario de Energía y Estado de Ánimo.
    </p>
</div>
""", unsafe_allow_html=True)

# Detección estricta de Telegram WebApp user_id vía parámetros de URL (st.query_params)
query_params = st.query_params
telegram_user_id = query_params.get("user_id", None)

user_filter = None

if telegram_user_id and str(telegram_user_id).isdigit():
    user_filter = int(telegram_user_id)
    st.sidebar.success(f"🔒 **Panel Privado de Usuario**\n\nID: `{user_filter}`")
else:
    # Si se accede directamente sin user_id desde Telegram, bloquemos la vista global por seguridad
    st.warning("🔒 **Acceso Privado Protegido**")
    st.info(
        "Para ver tus estadísticas personales de forma segura, por favor abre el Dashboard directamente desde tu conversación en Telegram usando el comando `/dashboard` o la Web App del menú."
    )
    st.stop()

# Filtro de rango de fechas
today = datetime.now().date()
default_start = today - timedelta(days=30)

col_d1, col_d2 = st.sidebar.columns(2)
with col_d1:
    fecha_inicio = st.date_input("Fecha Inicio", default_start)
with col_d2:
    fecha_fin = st.date_input("Fecha Fin", today)

ventana_media_movil = st.sidebar.slider(
    "Media Móvil (Días):",
    min_value=3,
    max_value=14,
    value=7,
    help="Define la ventana de días para calcular la tendencia de la media semanal."
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Consejo:** Registra tus datos diariamente en Telegram con `/registrar` para ver tendencias más precisas.")

# ==============================================================================
# CARGA Y PROCESAMIENTO DE DATOS
# ==============================================================================

@st.cache_data(ttl=60)
def fetch_data(user_id=None, start_str=None, end_str=None):
    if not db:
        return pd.DataFrame()
    registros = db.obtener_registros(
        user_id=user_id,
        fecha_inicio=start_str,
        fecha_fin=end_str
    )
    if not registros:
        return pd.DataFrame()
    
    df = pd.DataFrame(registros)
    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df.sort_values("fecha").reset_index(drop=True)
    return df


start_str = fecha_inicio.strftime("%Y-%m-%d")
end_str = fecha_fin.strftime("%Y-%m-%d")

df = fetch_data(user_id=user_filter, start_str=start_str, end_str=end_str)

if df.empty:
    st.warning("⚠️ No se encontraron registros para los filtros seleccionados. Registra datos desde Telegram o ajusta el rango de fechas.")
    
    # Generar datos demostrativos si está vacío
    st.markdown("### 🧪 Vista Previa de Ejemplo (Datos Simulados)")
    fechas_demo = pd.date_range(end=today, periods=14)
    df = pd.DataFrame({
        "fecha": fechas_demo,
        "energia": np.random.randint(4, 10, size=14),
        "humor": np.random.randint(5, 10, size=14),
        "comentarios": ["Día productivo", "Un poco cansado", "Excelente día", "Entrenamiento intenso", "Trabajo fluido", "", "Descanso activo", "", "", "", "", "", "", ""]
    })

# Procesamiento / Limpieza de datos (Métricas Semanales y Correlación)
df["energia_rolling"] = df["energia"].rolling(window=ventana_media_movil, min_periods=1).mean()
df["humor_rolling"] = df["humor"].rolling(window=ventana_media_movil, min_periods=1).mean()

# Cálculo del coeficiente de correlación de Pearson entre Energía y Humor
if len(df) > 1:
    correlacion = df["energia"].corr(df["humor"])
else:
    correlacion = 0.0

# ==============================================================================
# DASHBOARD: TARJETAS DE RESUMEN DE BIENESTAR (USER-FRIENDLY)
# ==============================================================================

col1, col2, col3, col4 = st.columns(4)

avg_energia = df['energia'].mean()
avg_humor = df['humor'].mean()

with col1:
    st.metric(
        label="⚡ Nivel de Energía",
        value=f"{avg_energia:.1f} / 10",
        delta="¡Muy buena energía!" if avg_energia >= 7 else "Energía moderada"
    )

with col2:
    st.metric(
        label="💖 Estado de Ánimo",
        value=f"{avg_humor:.1f} / 10",
        delta="¡Ánimo fantástico!" if avg_humor >= 7 else "Ánimo estable"
    )

with col3:
    # Explicación sencilla en lugar de "Coeficiente de Correlación de Pearson"
    if not pd.isna(correlacion) and correlacion > 0.4:
        relacion_text = "Tener más energía te sube mucho el ánimo 🚀"
    elif not pd.isna(correlacion) and correlacion > 0.1:
        relacion_text = "Tu energía y ánimo van bastante de la mano 🤝"
    else:
        relacion_text = "Tu ánimo es independiente de tu cansancio 🌈"

    st.metric(
        label="✨ Tu Patrón Principal",
        value=relacion_text
    )

with col4:
    st.metric(
        label="🗓️ Días Registrados",
        value=f"{len(df)} días",
        delta="¡Gran constancia!"
    )

st.markdown("---")

# ==============================================================================
# GRÁFICOS VISUALES Y CÁLIDOS (SIN TÉRMINOS TÉCNICOS)
# ==============================================================================

st.subheader("📊 Tu Evolución de Bienestar")

# Gráfico principal estilizado en Plotly
fig = go.Figure()

# Línea de Energía
fig.add_trace(go.Scatter(
    x=df["fecha"], y=df["energia_rolling"],
    mode="lines+markers",
    name="⚡ Energía",
    line=dict(color="#38bdf8", width=4, shape="spline"),
    marker=dict(size=8, color="#0284c7")
))

# Línea de Humor
fig.add_trace(go.Scatter(
    x=df["fecha"], y=df["humor_rolling"],
    mode="lines+markers",
    name="💖 Estado de Ánimo",
    line=dict(color="#f43f5e", width=4, shape="spline"),
    marker=dict(size=8, color="#be123c")
))

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(15,23,42,0.6)",
    height=400,
    margin=dict(l=20, r=20, t=30, b=20),
    yaxis=dict(range=[0, 10.5], title="Escala de Bienestar (1-10)"),
    xaxis=dict(title="Fecha"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

# ==============================================================================
# TABLA DE DATOS HISTÓRICOS Y EXPORTACIÓN
# ==============================================================================

st.markdown("---")
st.subheader("📋 Histórico de Registros")

col_search, col_export = st.columns([3, 1])
with col_search:
    search_term = st.text_input("🔍 Buscar en comentarios:", "")

filtered_df = df.copy()
if search_term:
    filtered_df = filtered_df[filtered_df["comentarios"].astype(str).str.contains(search_term, case=False, na=False)]

display_cols = ["fecha", "energia", "humor", "comentarios"]
if "user_id" in filtered_df.columns:
    display_cols.insert(1, "user_id")

st.dataframe(
    filtered_df[display_cols].sort_values("fecha", ascending=False),
    use_container_width=True,
    column_config={
        "fecha": st.column_config.DateColumn("Fecha", format="YYYY-MM-DD"),
        "energia": st.column_config.ProgressColumn("Energía", min_value=1, max_value=10, format="%d/10"),
        "humor": st.column_config.ProgressColumn("Humor", min_value=1, max_value=10, format="%d/10"),
        "comentarios": st.column_config.TextColumn("Comentarios")
    }
)

# Botón para descargar CSV
csv_data = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Descargar Histórico (CSV)",
    data=csv_data,
    file_name=f"registros_bot_bip_{today.strftime('%Y%m%d')}.csv",
    mime="text/csv"
)

# ==============================================================================
# INTEGRACIÓN DEL AI INSIGHTS AGENT (LLM REASONING)
# ==============================================================================

st.markdown("---")
st.subheader("🧠 AI Insights Agent (Diagnóstico de Bienestar con LLM)")

col_ai_info, col_ai_btn = st.columns([3, 1])

with col_ai_info:
    st.write(
        "Haz clic en el botón para solicitar a nuestro **AI Insights Agent** (impulsado por Google Gemini LLM) "
        "que analice tus tendencias de humor, energía y notas personales."
    )

with col_ai_btn:
    generar_reporte = st.button("✨ Generar Informe con IA", use_container_width=True)

if generar_reporte:
    with st.spinner("🤖 El AI Agent está analizando tus patrones de bienestar con LLM..."):
        try:
            from ai_insights.ai_agent import AIInsightsAgent
            agent = AIInsightsAgent()
            reporte_markdown = agent.analizar_tendencias(filtered_df.to_dict(orient="records"))
            
            st.markdown("### 📝 Reporte de Bienestar de la IA")
            st.info(reporte_markdown)
        except Exception as e:
            st.error(f"Error al invocar el AI Agent: {e}")

