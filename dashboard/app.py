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
    page_title="Bot-Bip | Resumen de Bienestar",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS personalizados para diseño premium
st.markdown("""
    <style>
    /* Optimizar espacios para pantallas móviles */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }
    
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
        return get_db_client(use_service_role=True)
    except Exception as e:
        st.error(f"Error conectando a Supabase: {e}")
        return None


db = init_db()

# Detección estricta de Telegram WebApp user_id y lang vía parámetros de URL (st.query_params)
query_params = st.query_params
telegram_user_id = query_params.get("user_id", None)
lang_code = query_params.get("lang", "es").lower()

if lang_code not in ["es", "en", "fr"]:
    lang_code = "es"

# Diccionario i18n para el Dashboard Streamlit
I18N_DASHBOARD = {
    "es": {
        "title": "🌸 Resumen de Bienestar",
        "subtitle": "Espacio personal para el seguimiento de tu estabilidad, estado de ánimo y descanso.",
        "sidebar_title": "🔒 **Panel Privado de Usuario**",
        "access_denied_title": "🔒 **Acceso Privado Protegido**",
        "access_denied_msg": "Para ver tus estadísticas personales de forma segura, por favor abre tu panel presionando el botón **📊 Abrir Mi Resumen de Bienestar** directamente desde tu conversación en Telegram usando el comando `/dashboard` o al finalizar un registro.",
        "start_date": "Fecha Inicio",
        "end_date": "Fecha Fin",
        "moving_avg": "Media Móvil (Días):",
        "moving_avg_help": "Define la ventana de días para calcular la tendencia de la media semanal.",
        "sidebar_tip": "💡 **Consejo:** Registra tus datos diariamente en Telegram con `/registrar` para ver tendencias más precisas.",
        "no_data_warning": "⚠️ No se encontraron registros para los filtros seleccionados. Registra datos desde Telegram o ajusta el rango de fechas.",
        "preview_title": "🧪 Vista Previa de Ejemplo (Datos Simulados)",
        "metric_energy": "⚡ Nivel de Energía",
        "metric_mood": "💖 Estado de Ánimo",
        "metric_sleep": "💤 Promedio Descanso",
        "metric_days": "🗓️ Días Registrados",
        "energy_high": "¡Muy buena energía!",
        "energy_mod": "Energía moderada",
        "mood_high": "¡Ánimo fantástico!",
        "mood_mod": "Ánimo estable",
        "sleep_good": "Descanso óptimo",
        "sleep_short": "Descanso corto ⚠️",
        "sleep_long": "Sueño prolongado",
        "consistency": "¡Gran constancia!",
        "chart_title": "📊 Tu Evolución de Bienestar & Descanso",
        "series_energy": "⚡ Energía",
        "series_mood": "💖 Ánimo",
        "series_sleep": "💤 Descanso (h)",
        "table_title": "📋 Histórico de Registros",
        "search_label": "🔍 Buscar en comentarios:",
        "col_date": "Fecha",
        "col_energy": "Energía",
        "col_mood": "Humor",
        "col_comments": "Comentarios",
        "pdf_download_btn": "📄 Descargar Informe Clínico (PDF)",
        "ai_title": "🌿 Asistente Inteligente de Bienestar",
        "ai_desc": "Recibe una lectura comprensiva y empática sobre la evolución de tu energía, estado de ánimo y descanso junto a pautas personalizadas de autocuidado.",
        "ai_tip": "💡 **¿En qué te ayuda?** Evalúa tus hábitos diarios para ayudarte a prevenir altibajos y mantener una rutina equilibrada de descanso.",
        "ai_btn": "✨ Analizar Mi Bienestar",
        "ai_spinner": "🌸 Observando tus patrones de energía y descanso... Un momento por favor...",
        "ai_success": "✅ **¡Análisis de Bienestar completado!**"
    },
    "en": {
        "title": "🌸 Wellness Summary",
        "subtitle": "Personal space to monitor your stability, mood, and sleep rest.",
        "sidebar_title": "🔒 **Private User Panel**",
        "access_denied_title": "🔒 **Protected Private Access**",
        "access_denied_msg": "To securely view your personal stats, please open your panel by tapping **📊 Open My Wellness Dashboard** directly from your Telegram conversation using the `/dashboard` command.",
        "start_date": "Start Date",
        "end_date": "End Date",
        "moving_avg": "Moving Average (Days):",
        "moving_avg_help": "Sets the window of days to compute the weekly trend.",
        "sidebar_tip": "💡 **Tip:** Log your daily data in Telegram with `/registrar` or `/log` to see accurate trends.",
        "no_data_warning": "⚠️ No entries found for the selected filters. Log data from Telegram or adjust the date range.",
        "preview_title": "🧪 Sample Preview (Simulated Data)",
        "metric_energy": "⚡ Energy Level",
        "metric_mood": "💖 Mood Status",
        "metric_sleep": "💤 Sleep Average",
        "metric_days": "🗓️ Days Logged",
        "energy_high": "Great energy level!",
        "energy_mod": "Moderate energy",
        "mood_high": "Fantastic mood!",
        "mood_mod": "Stable mood",
        "sleep_good": "Optimal sleep",
        "sleep_short": "Short sleep ⚠️",
        "sleep_long": "Long sleep",
        "consistency": "Great consistency!",
        "chart_title": "📊 Your Wellness & Sleep Progression",
        "series_energy": "⚡ Energy",
        "series_mood": "💖 Mood",
        "series_sleep": "💤 Sleep (h)",
        "table_title": "📋 Entry History",
        "search_label": "🔍 Search in notes:",
        "col_date": "Date",
        "col_energy": "Energy",
        "col_mood": "Mood",
        "col_comments": "Notes",
        "pdf_download_btn": "📄 Download Clinical PDF Report",
        "ai_title": "🌿 Intelligent Wellness Assistant",
        "ai_desc": "Get a empathetic and comprehensive analysis of your energy, mood, and sleep progression along with personalized care tips.",
        "ai_tip": "💡 **How it helps:** Evaluates your daily habits to prevent mood swings and maintain a balanced routine.",
        "ai_btn": "✨ Analyze My Wellness",
        "ai_spinner": "🌸 Observing your energy and sleep patterns... One moment please...",
        "ai_success": "✅ **Wellness Analysis Completed!**"
    },
    "fr": {
        "title": "🌸 Bilan de Bien-être",
        "subtitle": "Espace personnel pour le suivi de votre stabilité, humeur et sommeil.",
        "sidebar_title": "🔒 **Espace Utilisateur Privé**",
        "access_denied_title": "🔒 **Accès Privé Protégé**",
        "access_denied_msg": "Pour consulter vos statistiques personnelles en toute sécurité, veuillez ouvrir votre tableau de bord en appuyant sur le bouton **📊 Ouvrir Mon Tableau de Bord** depuis Telegram avec `/dashboard`.",
        "start_date": "Date de début",
        "end_date": "Date de fin",
        "moving_avg": "Moyenne mobile (Jours) :",
        "moving_avg_help": "Définit la fenêtre de jours pour calculer la tendance hebdomadaire.",
        "sidebar_tip": "💡 **Astuce :** Enregistrez vos données quotidiennement sur Telegram avec `/registrar`.",
        "no_data_warning": "⚠️ Aucun enregistrement trouvé pour les filtres sélectionnés.",
        "preview_title": "🧪 Aperçu d'exemple (Données simulées)",
        "metric_energy": "⚡ Niveau d'énergie",
        "metric_mood": "💖 État d'humeur",
        "metric_sleep": "💤 Sommeil moyen",
        "metric_days": "🗓️ Jours enregistrés",
        "energy_high": "Excellente énergie !",
        "energy_mod": "Énergie modérée",
        "mood_high": "Humeur fantastique !",
        "mood_mod": "Humeur stable",
        "sleep_good": "Sommeil optimal",
        "sleep_short": "Sommeil court ⚠️",
        "sleep_long": "Sommeil prolongé",
        "consistency": "Grande régularité !",
        "chart_title": "📊 Évolution de votre bien-être et sommeil",
        "series_energy": "⚡ Énergie",
        "series_mood": "💖 Humeur",
        "series_sleep": "💤 Sommeil (h)",
        "table_title": "📋 Historique des enregistrements",
        "search_label": "🔍 Rechercher dans les remarques :",
        "col_date": "Date",
        "col_energy": "Énergie",
        "col_mood": "Humeur",
        "col_comments": "Remarques",
        "pdf_download_btn": "📄 Télécharger le rapport clinique (PDF)",
        "ai_title": "🌿 Assistant intelligent de bien-être",
        "ai_desc": "Recevez une analyse bienveillante de votre énergie, humeur et sommeil ainsi que des conseils personnalisés.",
        "ai_tip": "💡 **En quoi cela vous aide ?** Évalue vos habitudes quotidiennes pour éviter les variations d'humeur.",
        "ai_btn": "✨ Analyser mon bien-être",
        "ai_spinner": "🌸 Analyse de vos données en cours... Un instant s'il vous plaît...",
        "ai_success": "✅ **Analyse de bien-être terminée !**"
    }
}

t_dash = I18N_DASHBOARD[lang_code]

# ==============================================================================
# ENCABEZADO Y BARRA LATERAL (FILTROS)
# ==============================================================================

st.markdown(f"""
<div class="dashboard-header">
    <h1 class="dashboard-title">{t_dash['title']}</h1>
    <p style="color: #94a3b8; margin-top: 8px; margin-bottom: 0;">
        {t_dash['subtitle']}
    </p>
</div>
""", unsafe_allow_html=True)

user_filter = None

if telegram_user_id and str(telegram_user_id).isdigit():
    user_filter = int(telegram_user_id)
    st.sidebar.success(f"{t_dash['sidebar_title']}\n\nID: `{user_filter}`")
else:
    # Si se accede directamente sin user_id desde Telegram, bloquemos la vista global por seguridad
    st.warning(t_dash["access_denied_title"])
    st.info(t_dash["access_denied_msg"])
    st.stop()

# Filtro de rango de fechas
today = datetime.now().date()
default_start = today - timedelta(days=30)

col_d1, col_d2 = st.sidebar.columns(2)
with col_d1:
    fecha_inicio = st.date_input(t_dash["start_date"], default_start)
with col_d2:
    fecha_fin = st.date_input(t_dash["end_date"], today)

ventana_media_movil = st.sidebar.slider(
    t_dash["moving_avg"],
    min_value=3,
    max_value=14,
    value=7,
    help=t_dash["moving_avg_help"]
)

st.sidebar.markdown("---")
st.sidebar.info(t_dash["sidebar_tip"])

# ==============================================================================
# CARGA Y PROCESAMIENTO DE DATOS
# ==============================================================================

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
    if "comentarios" in df.columns:
        from db.supabase_client import decrypt_val
        df["comentarios"] = df["comentarios"].apply(lambda x: decrypt_val(x) if isinstance(x, str) else x)

    if "created_at" in df.columns:
        df["created_at_dt"] = pd.to_datetime(df["created_at"])
        df = df.sort_values("created_at_dt").reset_index(drop=True)
    else:
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
avg_sueno = df['sueno_horas'].mean() if "sueno_horas" in df.columns else 8.0

with col1:
    st.metric(
        label=t_dash["metric_energy"],
        value=f"{avg_energia:.1f} / 10",
        delta=t_dash["energy_high"] if avg_energia >= 7 else t_dash["energy_mod"]
    )

with col2:
    st.metric(
        label=t_dash["metric_mood"],
        value=f"{avg_humor:.1f} / 10",
        delta=t_dash["mood_high"] if avg_humor >= 7 else t_dash["mood_mod"]
    )

with col3:
    st.metric(
        label=t_dash["metric_sleep"],
        value=f"{avg_sueno:.1f}h",
        delta=t_dash["sleep_good"] if 7 <= avg_sueno <= 9 else (t_dash["sleep_short"] if avg_sueno < 6 else t_dash["sleep_long"])
    )

with col4:
    st.metric(
        label=t_dash["metric_days"],
        value=f"{len(df)} days" if lang_code == "en" else (f"{len(df)} jours" if lang_code == "fr" else f"{len(df)} días"),
        delta=t_dash["consistency"]
    )

st.markdown("---")

# ==============================================================================
# GRÁFICOS VISUALES Y CÁLIDOS (PUNTOS Y LÍNEAS CLARAS)
# ==============================================================================

st.subheader(t_dash["chart_title"])

# Si hay múltiples registros en el mismo día o varios puntos, preparar el DataFrame
chart_df = df.copy()

# Crear etiquetas legibles para el eje X en hora local (España / UTC+2)
if "created_at" in chart_df.columns:
    chart_df["momento_dt"] = pd.to_datetime(chart_df["created_at"])
    if chart_df["momento_dt"].dt.tz is None:
        chart_df["momento_dt"] = chart_df["momento_dt"].dt.tz_localize("UTC").dt.tz_convert("Europe/Madrid")
    else:
        chart_df["momento_dt"] = chart_df["momento_dt"].dt.tz_convert("Europe/Madrid")
    
    chart_df["momento"] = chart_df["momento_dt"].dt.strftime("%d/%m %H:%M")
else:
    chart_df["momento"] = pd.to_datetime(chart_df["fecha"]).dt.strftime("%d/%m")

chart_cols_map = {"energia": t_dash["series_energy"], "humor": t_dash["series_mood"]}
if "sueno_horas" in chart_df.columns:
    chart_cols_map["sueno_horas"] = t_dash["series_sleep"]

chart_df_melted = chart_df.melt(
    id_vars=["momento"], 
    value_vars=list(chart_cols_map.keys()),
    var_name="Métrica", 
    value_name="Valor"
)
chart_df_melted["Métrica"] = chart_df_melted["Métrica"].map(chart_cols_map)

import plotly.express as px

color_map = {}
color_map[t_dash["series_energy"]] = "#38bdf8"
color_map[t_dash["series_mood"]] = "#f43f5e"
if "sueno_horas" in chart_df.columns:
    color_map[t_dash["series_sleep"]] = "#a855f7"

fig = px.line(
    chart_df_melted,
    x="momento",
    y="Valor",
    color="Métrica",
    markers=True,
    color_discrete_map=color_map
)

fig.update_layout(
    template="plotly_dark",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=10, b=10),
    height=340,
    hovermode="x unified",
    dragmode=False,
    xaxis=dict(
        title=None, 
        showgrid=True, 
        gridcolor="#334155",
        fixedrange=True,
        type="category"
    ),
    yaxis=dict(
        title=None, 
        range=[0, 11], 
        showgrid=True, 
        gridcolor="#334155",
        fixedrange=True
    ),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=None)
)

fig.update_traces(
    line=dict(width=3), 
    marker=dict(size=12, symbol="circle", opacity=1)
)

st.plotly_chart(
    fig, 
    use_container_width=True, 
    config={
        "displayModeBar": False, 
        "scrollZoom": False,
        "doubleClick": False,
        "showAxisDragHandles": False,
        "staticPlot": False
    }
)

# ==============================================================================
# TABLA DE DATOS HISTÓRICOS Y EXPORTACIÓN
# ==============================================================================

st.markdown("---")
st.subheader(t_dash["table_title"])

col_search, col_export = st.columns([3, 1])
with col_search:
    search_term = st.text_input(t_dash["search_label"], "")

filtered_df = df.copy()
if search_term:
    filtered_df = filtered_df[filtered_df["comentarios"].astype(str).str.contains(search_term, case=False, na=False)]

display_cols = ["fecha", "energia", "humor", "comentarios"]
if "user_id" in filtered_df.columns:
    display_cols.insert(1, "user_id")

if "comentarios" in filtered_df.columns:
    from db.supabase_client import decrypt_val
    filtered_df["comentarios"] = filtered_df["comentarios"].apply(lambda x: decrypt_val(x) if isinstance(x, str) else x)

st.dataframe(
    filtered_df[display_cols].sort_values("fecha", ascending=False),
    use_container_width=True,
    column_config={
        "fecha": st.column_config.DateColumn(t_dash["col_date"], format="YYYY-MM-DD"),
        "energia": st.column_config.ProgressColumn(t_dash["col_energy"], min_value=1, max_value=10, format="%d/10"),
        "humor": st.column_config.ProgressColumn(t_dash["col_mood"], min_value=1, max_value=10, format="%d/10"),
        "comentarios": st.column_config.TextColumn(t_dash["col_comments"])
    }
)

try:
    import importlib
    import ai_insights.pdf_generator as pdf_gen_module
    importlib.reload(pdf_gen_module)
    pdf_bytes = pdf_gen_module.generar_pdf_clinico(filtered_df)
    st.download_button(
        label=t_dash["pdf_download_btn"],
        data=pdf_bytes,
        file_name=f"informe_medico_bienestar_{today.strftime('%Y_%m_%d')}.pdf",
        mime="application/pdf",
        use_container_width=True,
        key=f"pdf_btn_v3_{len(filtered_df)}"
    )
except Exception as pdf_err:
    st.error(f"⚠️ Error al preparar el PDF: {pdf_err}")

# ==============================================================================
# INTEGRACIÓN DEL AI INSIGHTS AGENT (ANÁLISIS DE IA USER-FRIENDLY)
# ==============================================================================

st.markdown("---")

with st.container():
    st.markdown(f"### {t_dash['ai_title']}")
    st.markdown(t_dash["ai_desc"])
    
    col_ai_card1, col_ai_card2 = st.columns([2, 1])
    
    with col_ai_card1:
        st.caption(t_dash["ai_tip"])
    
    with col_ai_card2:
        generar_reporte = st.button(t_dash["ai_btn"], use_container_width=True, type="primary")

if generar_reporte:
    with st.spinner(t_dash["ai_spinner"]):
        try:
            import importlib
            import ai_insights.ai_agent as ai_module
            importlib.reload(ai_module)
            agent = ai_module.AIInsightsAgent()
            reporte_markdown = agent.analizar_tendencias(filtered_df.to_dict(orient="records"))
            
            st.success(t_dash["ai_success"])
            
            # Tarjeta de lectura limpia
            st.markdown(
                f"""
                <div style="background-color: #F8FAFC; border-left: 4px solid #6366F1; padding: 18px; border-radius: 8px; margin-top: 10px;">
                    {reporte_markdown}
                </div>
                """,
                unsafe_allow_html=True
            )
        except Exception as e:
            st.error(f"Ocurrió un inconveniente al conectar con el Asistente de IA: {e}")

