# Bot-Bip Agents Architecture

Este proyecto está organizado en 4 agentes/módulos especializados para facilitar su desarrollo, mantenimiento y escalabilidad.

---

## 1. 🗄️ Database & Security Agent (`db/` & `schema.sql`)
- **Archivo principal de esquema:** [`schema.sql`](file:///home/gabriel/Bot-Bip/schema.sql)
- **Cliente de conexión:** [`db/supabase_client.py`](file:///home/gabriel/Bot-Bip/db/supabase_client.py)
- **Responsabilidades:**
  - Definición del esquema PostgreSQL de la tabla `registros_diarios`.
  - Configuración de políticas de seguridad Row Level Security (RLS) e índices de búsqueda.
  - Abstracción de operaciones CRUD (inserción, actualización y consulta) con Supabase.

---

## 2. 🤖 Telegram Bot Agent (`bot/`)
- **Script principal:** [`bot/telegram_bot.py`](file:///home/gabriel/Bot-Bip/bot/telegram_bot.py)
- **Responsabilidades:**
  - Gestión de la interfaz conversacional mediante `ConversationHandler`.
  - Recolección secuencial de métricas diarias (energía, humor y comentarios).
  - Integración con el cliente de Supabase para guardar datos en tiempo real.
  - Sistema de alertas/recordatorios diarios para el registro de datos.

---

## 3. 📊 Dashboard & Analytics Agent (`dashboard/`)
- **Script de la aplicación web:** [`dashboard/app.py`](file:///home/gabriel/Bot-Bip/dashboard/app.py)
- **Responsabilidades:**
  - Visualización interactiva construida con **Streamlit**.
  - Cálculo de promedios semanales/mensuales y tendencias temporales.
  - Análisis de correlación entre los niveles de energía y humor.
  - Filtros interactivos por rango de fechas y exportación de datos.

---

## 4. 🚀 DevOps & Deployment Agent (`Dockerfile`, `Procfile`, `.env`)
- **Configuraciones:** [`Dockerfile`](file:///home/gabriel/Bot-Bip/Dockerfile), [`Procfile`](file:///home/gabriel/Bot-Bip/Procfile), [`requirements.txt`](file:///home/gabriel/Bot-Bip/requirements.txt)
- **Responsabilidades:**
  - Gestión de dependencias y variables de entorno (`.env`).
  - Configuración para despliegue 24/7 en servicios de nube gratuitos (Render, Railway, Fly.io).

---

## 5. 🛡️ Health & Communication Supervisor Agent (`supervisor/`)
- **Script principal:** [`supervisor/health_checker.py`](file:///home/gabriel/Bot-Bip/supervisor/health_checker.py)
- **Responsabilidades:**
  - Monitorizar periódicamente el estado operativo de los agentes (Supabase, Bot de Telegram y Dashboard de Streamlit).
  - Facilitar la comunicación de diagnósticos entre agentes en caso de fallo.
  - Generar un reporte detallado con la causa raíz y la **solución propuesta**.
  - Notificar y solicitar **confirmación del usuario** antes de aplicar cualquier acción correctiva.

---

## 6. 🧠 AI Insights & Analytics Agent (`ai_insights/`)
- **Script principal:** [`ai_insights/ai_agent.py`](file:///home/gabriel/Bot-Bip/ai_insights/ai_agent.py)
- **Responsabilidades:**
  - Analizar las tendencias históricas de bienestar (energía, humor y comentarios) utilizando Modelos de Lenguaje (LLM como Google Gemini).
  - Generar reportes analíticos estructurados, detección de patrones y recomendaciones personalizadas.
  - Integración modular con el Dashboard para consumo bajo demanda.
