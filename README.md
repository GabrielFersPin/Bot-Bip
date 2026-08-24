# 🌸 Bot-Bip: Asistente & Monitor de Bienestar Psicoafectivo 🧠⚡

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Telegram Bot API](https://img.shields.io/badge/Telegram%20Bot%20API-v20+-0088cc.svg)](https://python-telegram-bot.org/)
[![Supabase DB](https://img.shields.io/badge/Database-Supabase%20PostgreSQL-green.svg)](https://supabase.com/)

**Bot-Bip** es una herramienta digital de salud mental diseñada para acompañar y registrar de manera sencilla y compasiva la estabilidad emocional, energía, descanso e higiene del sueño diaria de personas con Trastorno Bipolar o fluctuaciones del estado de ánimo.

---

## 💖 Proyecto Comunitario & Donaciones

Este proyecto es **100% de código abierto, gratuito e impulsado por la comunidad**. No cobramos suscripciones a los usuarios para garantizar que cualquier persona que lo necesite tenga acceso libre a sus datos de bienestar y herramientas de prevención.

Si este bot te ha resultado útil o quieres ayudar a mantener el servidor de despliegue 24/7 y la infraestructura en la nube encendidos, puedes apoyar con una donación voluntaria:

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Donate%20💖-orange.svg?style=for-the-badge&logo=buy-me-a-coffee)](https://www.buymeacoffee.com/)
[![GitHub Sponsors](https://img.shields.io/badge/Sponsor%20on-GitHub-ea4aaa.svg?style=for-the-badge&logo=github)](https://github.com/sponsors)

---

## 🌟 Características Principales

1. ⚡ **Check-in Diario Inclusivo:** Registro guiado en 30 segundos (Energía, Ánimo, Horas de descanso y Adherencia a Medicación).
2. 📄 **Informes Clínicos PDF Directos (`/informe`):** Generación automática de reportes en PDF vectorial listos para presentar en la consulta de psiquiatría o psicología.
3. 🌸 **Resumen Semanal Motivacional (`/resumen_semanal`):** Cálculo de tendencias y promedios de los últimos 7 días.
4. 💙 **Red de Apoyo & Notificación de Acompañamiento:** Si la persona no realiza registros en 3 días (debido a un bajón o cansancio), el bot notifica compasivamente a sus personas de confianza registradas (`/contacto`).
5. 📊 **Panel Web Interactivo (Streamlit):** Gráficos de tendencias, correlaciones y diagnósticos mediante IA (Google Gemini / Groq).

---

## 🚀 Arquitectura del Proyecto

El proyecto está organizado en 6 agentes/módulos especializados:
- `bot/`: Agente de interfaz conversacional de Telegram (`python-telegram-bot`).
- `db/`: Agente de persistencia y seguridad con PostgreSQL + Supabase.
- `dashboard/`: Agente de analítica visual interactiva en Streamlit.
- `ai_insights/`: Motor analítico de resiliencia e informe PDF vectorial.
- `supervisor/`: Diagnóstico y monitorización del estado de salud del sistema.

---

## 🛠️ Instalación y Uso Local

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/GabrielFersPin/Bot-Bip.git
   cd Bot-Bip
   ```

2. **Crear entorno virtual e instalar dependencias:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno (`.env`):**
   Crea un archivo `.env` basado en la plantilla de configuración:
   ```env
   TELEGRAM_BOT_TOKEN="tu_token_de_telegram"
   SUPABASE_URL="tu_url_de_supabase"
   SUPABASE_ANON_KEY="tu_clave_anonima"
   DASHBOARD_URL="http://localhost:8501"
   ```

4. **Iniciar el bot y el panel:**
   ```bash
   python main.py
   streamlit run dashboard/app.py
   ```

---

## 📜 Licencia

Este proyecto está bajo la Licencia **MIT** - consulta el archivo [LICENSE](LICENSE) para más detalles.

---
*Construido con empatía y tecnología para la comunidad de Salud Mental.* 🌸
