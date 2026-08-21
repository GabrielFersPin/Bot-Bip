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

# Detección de Telegram WebApp user_id vía parámetros de URL (st.query_params)
query_params = st.query_params
telegram_user_id = query_params.get("user_id", None)

user_filter = None

if telegram_user_id and str(telegram_user_id).isdigit():
    user_filter = int(telegram_user_id)
    st.sidebar.success(f"🔒 **Panel Privado** (ID Usuario: {user_filter})")
else:
    st.sidebar.header("🔍 Filtros & Configuración")
    # Cargar lista de usuarios si no viene de una WebApp privada de Telegram
    if db:
        usuarios_disponibles = db.obtener_usuarios_unicos()
    else:
        usuarios_disponibles = []

    if usuarios_disponibles:
        user_options = ["Todos los usuarios"] + [str(u) for u in usuarios_disponibles]
        selected_user_str = st.sidebar.selectbox("Seleccionar Usuario (ID):", user_options)
        if selected_user_str != "Todos los usuarios":
            user_filter = int(selected_user_str)

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
# DASHBOARD: KPIs Y MÉTRICAS CLAVE
# ==============================================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="⚡ Promedio Energía",
        value=f"{df['energia'].mean():.1f} / 10",
        delta=f"Última: {df['energia'].iloc[-1]}" if not df.empty else None
    )

with col2:
    st.metric(
        label="🎭 Promedio Humor",
        value=f"{df['humor'].mean():.1f} / 10",
        delta=f"Última: {df['humor'].iloc[-1]}" if not df.empty else None
    )

with col3:
    if pd.isna(correlacion):
        corr_label = "N/A"
    else:
        corr_label = f"{correlacion:+.2f}"
    
    # Interpretación cualitativa de correlación
    if not pd.isna(correlacion) and correlacion > 0.5:
        corr_desc = "Fuerte Positiva"
    elif not pd.isna(correlacion) and correlacion > 0.2:
        corr_desc = "Moderada Positiva"
    elif not pd.isna(correlacion) and correlacion < -0.2:
        corr_desc = "Inversa / Negativa"
    else:
        corr_desc = "Sin Correlación Clara"

    st.metric(
        label="🔗 Correlación Energía-Humor",
        value=corr_label,
        delta=corr_desc
    )

with col4:
    st.metric(
        label="📅 Total Registros",
        value=str(len(df)),
        delta=f"Días evaluados"
    )

st.markdown("---")

# ==============================================================================
# GRÁFICOS INTERACTIVOS (ST.LINE_CHART Y PLOTLY)
# ==============================================================================

st.subheader("📈 Evolución Temporal: Energía vs. Humor")

# Pestañas para elegir vista gráfica
tab1, tab2, tab3 = st.tabs(["📉 Tendencias en Línea (Media Móvil)", "📊 Comparativa st.line_chart", "🎯 Matriz de Correlación (Scatter)"])

with tab1:
    fig = go.Figure()
    
    # Serie original Energía
    fig.add_trace(go.Scatter(
        x=df["fecha"], y=df["energia"],
        mode="markers+lines",
        name="Energía Diaria",
        line=dict(color="#38bdf8", width=1.5, dash="dot"),
        marker=dict(size=6)
    ))
    
    # Media móvil Energía
    fig.add_trace(go.Scatter(
        x=df["fecha"], y=df["energia_rolling"],
        mode="lines",
        name=f"Energía (Media {ventana_media_movil}d)",
        line=dict(color="#0284c7", width=3)
    ))

    # Serie original Humor
    fig.add_trace(go.Scatter(
        x=df["fecha"], y=df["humor"],
        mode="markers+lines",
        name="Humor Diario",
        line=dict(color="#f43f5e", width=1.5, dash="dot"),
        marker=dict(size=6)
    ))

    # Media móvil Humor
    fig.add_trace(go.Scatter(
        x=df["fecha"], y=df["humor_rolling"],
        mode="lines",
        name=f"Humor (Media {ventana_media_movil}d)",
        line=dict(color="#be123c", width=3)
    ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=450,
        margin=dict(l=20, r=20, t=30, b=20),
        yaxis=dict(range=[0, 10.5], title="Escala (1-10)"),
        xaxis=dict(title="Fecha"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.caption("Gráfico ligero nativo con `st.line_chart`:")
    chart_data = df.set_index("fecha")[["energia", "humor", "energia_rolling", "humor_rolling"]]
    chart_data.columns = ["Energía", "Humor", "Media Energía", "Media Humor"]
    st.line_chart(chart_data)

with tab3:
    st.caption("Dispersión y regresión lineal entre nivel de energía y estado de ánimo:")
    fig_scatter = px.scatter(
        df,
        x="energia",
        y="humor",
        trendline="ols" if len(df) > 2 else None,
        hover_data=["fecha", "comentarios"],
        labels={"energia": "Nivel de Energía (1-10)", "humor": "Nivel de Humor (1-10)"},
        title="Relación entre Energía y Humor",
        color="energia",
        color_continuous_scale="Blues"
    )
    fig_scatter.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=420
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

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

