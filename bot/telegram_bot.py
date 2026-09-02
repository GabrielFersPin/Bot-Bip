import os
import sys
import logging
from datetime import datetime, time
from typing import Dict, Any

# Asegurar que la raíz del proyecto esté en el PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    BotCommand
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

from db.supabase_client import get_db_client
from i18n import t, resolve_lang_code

# Configuración de Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Estados de la conversación
ENERGIA, HUMOR, SUENO, MEDICACION, COMENTARIOS = range(5)

def get_user_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Obtiene el idioma preferido del usuario (desde context.user_data o update.effective_user)."""
    if context and context.user_data and "lang" in context.user_data:
        return context.user_data["lang"]
    if update and update.effective_user and update.effective_user.language_code:
        return resolve_lang_code(update.effective_user.language_code)
    return "es"

def get_medicacion_keyboard(lang: str = "es") -> InlineKeyboardMarkup:
    """Genera teclado para consultar adherencia a la medicación en el idioma del usuario."""
    keyboard = [
        [InlineKeyboardButton(t("med_si", lang), callback_data="med_si"), InlineKeyboardButton(t("med_parcial", lang), callback_data="med_parcial")],
        [InlineKeyboardButton(t("med_no", lang), callback_data="med_no"), InlineKeyboardButton(t("med_skip", lang), callback_data="med_skip")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_sueno_keyboard() -> InlineKeyboardMarkup:
    """Genera un teclado en línea para seleccionar horas de sueño/descanso."""
    keyboard = [
        [InlineKeyboardButton("< 4h ⚠️", callback_data="sueno_3.0"), InlineKeyboardButton("5h - 6h 🌙", callback_data="sueno_5.5")],
        [InlineKeyboardButton("7h - 8h 💤", callback_data="sueno_7.5"), InlineKeyboardButton("9h - 10h 🛌", callback_data="sueno_9.5")],
        [InlineKeyboardButton("> 11h 💤", callback_data="sueno_11.0")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def calma_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /calma - Espacio de apoyo rápido con acceso directo a la Red de Apoyo."""
    user_id = update.effective_user.id
    lang = get_user_language(update, context)
    contactos = db.obtener_contactos_emergencia(user_id)

    keyboard = []
    text_contactos = ""

    if contactos:
        text_contactos = t("calma_contacts_header", lang)
        for c in contactos:
            nombre = c.get("nombre")
            telefono = c.get("telefono", "").replace(" ", "").replace("-", "")
            relacion = c.get("relacion", "Apoyo")
            text_contactos += f"• **{nombre}** ({relacion}): `{telefono}`\n"
            
            import urllib.parse
            mensaje_apoyo = "Hello, I am going through a tough moment and need support." if lang == "en" else ("Bonjour, je traverse un moment difficile." if lang == "fr" else f"Hola {nombre}, estoy pasando por un momento difícil y necesito apoyo.")
            mensaje_encoded = urllib.parse.quote_plus(mensaje_apoyo)
            
            clean_phone = telefono.replace("+", "")
            keyboard.append([
                InlineKeyboardButton(t("calma_btn_msg", lang).format(nombre=nombre), url=f"https://wa.me/{clean_phone}?text={mensaje_encoded}")
            ])
    else:
        text_contactos = t("calma_contact_tip", lang)

    calma_text = t("calma_title", lang) + f"{text_contactos}"

    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    await update.message.reply_text(calma_text, parse_mode="Markdown", reply_markup=reply_markup)


async def contacto_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /contacto - Permite registrar un número de teléfono de la red de apoyo."""
    user_id = update.effective_user.id
    lang = get_user_language(update, context)

    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            t("contacto_usage", lang),
            parse_mode="Markdown"
        )
        return

    nombre = context.args[0]
    telefono = context.args[1]
    relacion = context.args[2] if len(context.args) > 2 else "Red de Apoyo"

    res = db.guardar_contacto_emergencia(user_id=user_id, nombre=nombre, telefono=telefono, relacion=relacion)

    if res.get("success"):
        await update.message.reply_text(
            t("contacto_saved", lang).format(nombre=nombre, telefono=telefono, relacion=relacion),
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(f"❌ Error: `{res.get('error')}`", parse_mode="Markdown")


async def humor_step(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Procesa la respuesta de HUMOR e inicia la pregunta de SUEÑO."""
    val = None
    if update.callback_query:
        await update.callback_query.answer()
        data = update.callback_query.data
        if data.startswith("humor_"):
            val = int(data.split("_")[1])
    elif update.message and update.message.text:
        text = update.message.text.strip()
        if text.isdigit():
            val = int(text)

    if val is None or not (1 <= val <= 10):
        msg = "⚠️ Por favor, ingresa un número válido entre **1 y 10** para el humor."
        if update.callback_query:
            await update.callback_query.edit_message_text(msg, parse_mode="Markdown", reply_markup=get_rating_keyboard("humor"))
        else:
            await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_rating_keyboard("humor"))
        return HUMOR

    context.user_data["humor"] = val

    sueno_text = (
        f"✅ Humor guardado: **{val}/10**\n\n"
        "💤 **¿Cuántas horas aproximadas has dormido/descansado anoche?**\n"
        "*(El descanso es el marcador biológico principal para tu estabilidad)*:"
    )

    if update.callback_query:
        await update.callback_query.edit_message_text(
            sueno_text,
            parse_mode="Markdown",
            reply_markup=get_sueno_keyboard()
        )
    else:
        await update.message.reply_text(
            sueno_text,
            parse_mode="Markdown",
            reply_markup=get_sueno_keyboard()
        )

    return SUENO


async def sueno_step(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Procesa las horas de SUEÑO e inicia la pregunta de COMENTARIOS."""
    val = 8.0
    if update.callback_query:
        await update.callback_query.answer()
        data = update.callback_query.data
        if data.startswith("sueno_"):
            val = float(data.split("_")[1])
    elif update.message and update.message.text:
        text = update.message.text.strip().replace(",", ".")
        try:
            val = float(text)
        except ValueError:
            val = 8.0

    context.user_data["sueno_horas"] = val

    med_text = (
        f"✅ Descanso guardado: **{val}h**\n\n"
        "💊 **¿Has tomado tu medicación prescrita hoy?**"
    )

    if update.callback_query:
        await update.callback_query.edit_message_text(
            med_text,
            parse_mode="Markdown",
            reply_markup=get_medicacion_keyboard()
        )
    else:
        await update.message.reply_text(
            med_text,
            parse_mode="Markdown",
            reply_markup=get_medicacion_keyboard()
        )

    return MEDICACION


async def medicacion_step(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Procesa la respuesta sobre la medicación y pasa al paso de comentarios."""
    med_val = "Omitido"
    if update.callback_query:
        await update.callback_query.answer()
        data = update.callback_query.data
        if data == "med_si":
            med_val = "Sí"
        elif data == "med_parcial":
            med_val = "Parcial"
        elif data == "med_no":
            med_val = "No"

    context.user_data["medicacion"] = med_val

    comment_text = (
        f"✅ Medicación: **{med_val}**\n\n"
        "📝 **¿Quieres agregar algún comentario u observación sobre tu día?**\n"
        "(Escribe tus notas en un mensaje o presiona el botón para omitir):"
    )

    if update.callback_query:
        await update.callback_query.edit_message_text(
            comment_text,
            parse_mode="Markdown",
            reply_markup=get_skip_keyboard()
        )
    else:
        await update.message.reply_text(
            comment_text,
            parse_mode="Markdown",
            reply_markup=get_skip_keyboard()
        )

    return COMENTARIOS


async def comentarios_step(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Procesa el comentario final y guarda todo en Supabase con alertas precoces."""
    user_id = update.effective_user.id
    comentario = ""

    if update.callback_query:
        await update.callback_query.answer()
        if update.callback_query.data == "skip_comments":
            comentario = ""
    elif update.message and update.message.text:
        comentario = update.message.text.strip()

    energia = context.user_data.get("energia", 5)
    humor = context.user_data.get("humor", 5)
    sueno_horas = context.user_data.get("sueno_horas", 8.0)
    medicacion = context.user_data.get("medicacion", "Omitido")

    # Concatenar estado de medicación en las notas si se ha respondido
    comentario_final = comentario
    if medicacion != "Omitido":
        comentario_final = f"[Medicacion: {medicacion}] {comentario}".strip()

    # Guardar en Supabase
    result = db.guardar_registro_diario(
        user_id=user_id,
        energia=energia,
        humor=humor,
        sueno_horas=sueno_horas,
        comentarios=comentario_final
    )

    context.user_data.clear()

    # Detección precoz de alertas clínicas (Virajes de fase)
    alerta_text = ""
    if energia >= 9 and sueno_horas <= 4:
        alerta_text = (
            "\n\n⚠️ **Aviso de Bienestar:** Notamos alta energía (9-10) with muy pocas horas de descanso (<4h). "
            "Intenta tomar un espacio de relajación hoy con `/calma`."
        )
    elif energia <= 3 and humor <= 3:
        alerta_text = (
            "\n\n💙 **Aviso de Apoyo:** Tu nivel de energía y ánimo están bajos hoy. "
            "Sé amable contigo mismo/a. Si lo necesitas, busca a personas de confianza o usa el comando `/calma`."
        )

    url_base = os.getenv("DASHBOARD_URL", "http://localhost:8501")
    url_personalizada = f"{url_base}?user_id={user_id}"

    btn_dashboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Abrir Mi Resumen de Bienestar", url=url_personalizada)]
    ])

    if result.get("success"):
        summary_text = (
            "🎉 **¡Registro Guardado con Éxito!**\n\n"
            f"⚡ **Energía:** {energia}/10\n"
            f"🎭 **Humor:** {humor}/10\n"
            f"💤 **Descanso:** {sueno_horas}h\n"
            f"💊 **Medicación:** {medicacion}\n"
            f"📝 **Notas:** {comentario if comentario else 'Sin comentarios'}"
            f"{alerta_text}"
        )
        reply_markup = btn_dashboard
    else:
        summary_text = (
            "❌ Hubo un inconveniente al guardar tu registro en la base de datos.\n"
            f"Detalle: `{result.get('error')}`"
        )
        reply_markup = None

    if update.callback_query:
        await update.callback_query.edit_message_text(summary_text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text(summary_text, parse_mode="Markdown", reply_markup=reply_markup)

    return ConversationHandler.END

# Instancia del cliente de Supabase (usando Service Role para backend seguro)
try:
    db = get_db_client(use_service_role=True)
except Exception as err:
    logger.warning(f"No se pudo inicializar Supabase con Service Role Key: {err}. Intentando con Anon Key...")
    db = get_db_client(use_service_role=False)


def get_rating_keyboard(prefix: str) -> InlineKeyboardMarkup:
    """Genera un teclado en línea con botones del 1 al 10 en dos filas."""
    keyboard = [
        [InlineKeyboardButton(str(i), callback_data=f"{prefix}_{i}") for i in range(1, 6)],
        [InlineKeyboardButton(str(i), callback_data=f"{prefix}_{i}") for i in range(6, 11)],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_skip_keyboard() -> InlineKeyboardMarkup:
    """Genera un botón para omitir los comentarios."""
    keyboard = [[InlineKeyboardButton("⏭️ Omitir / Sin comentarios", callback_data="skip_comments")]]
    return InlineKeyboardMarkup(keyboard)


# ==============================================================================
# COMANDOS PRINCIPALES
# ==============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Comando /start - Da la bienvenida e inicia el primer check-in diario en el idioma del usuario."""
    lang = get_user_language(update, context)
    btn = InlineKeyboardMarkup([[InlineKeyboardButton(t("btn_register_now", lang), callback_data="iniciar_registro_ahora")]])
    await update.message.reply_text(
        t("welcome_start", lang),
        parse_mode="Markdown",
        reply_markup=btn
    )
    return ConversationHandler.END


async def registrar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Comando /registrar o botón de recordatorio - Inicia el flujo de preguntas en el idioma del usuario."""
    lang = get_user_language(update, context)
    text = t("energy_title", lang)
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_rating_keyboard("energia")
        )
    else:
        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_rating_keyboard("energia")
        )
    return ENERGIA


async def dashboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /dashboard - Envia enlace nativo a Streamlit filtrado por el ID del usuario y su idioma."""
    user_id = update.effective_user.id
    lang = get_user_language(update, context)
    url_base = os.getenv("DASHBOARD_URL", "http://localhost:8501")
    url_personalizada = f"{url_base}?user_id={user_id}&lang={lang}"
    keyboard = [
        [InlineKeyboardButton(t("dashboard_btn", lang), url=url_personalizada)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        t("dashboard_msg", lang),
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /stats - Muestra métricas globales del bot únicamente al Administrador."""
    user_id = update.effective_user.id
    admin_id_str = os.getenv("ADMIN_USER_ID", "")

    # Si está configurado ADMIN_USER_ID, restringir acceso exclusivo al administrador
    if admin_id_str and str(user_id) != admin_id_str.strip():
        await update.message.reply_text("🔒 Este comando es privado y está reservado para la administración del sistema.")
        return

    try:
        registros = db.obtener_registros()
        total_registros = len(registros)

        # Agrupar registros por user_id
        conteo_por_usuario = {}
        for r in registros:
            uid = r.get("user_id")
            if uid:
                conteo_por_usuario[uid] = conteo_por_usuario.get(uid, 0) + 1

        total_usuarios = len(conteo_por_usuario)

        detalle_usuarios = ""
        for idx, (uid, count) in enumerate(conteo_por_usuario.items(), 1):
            detalle_usuarios += f"  {idx}. `ID: {uid}` — **{count}** registro(s)\n"

        msg = (
            f"📊 **Métricas de Uso de Bot-Bip (Administración)**\n\n"
            f"👥 **Usuarios Totales:** {total_usuarios}\n"
            f"📝 **Registros Diarios Totales:** {total_registros}\n\n"
            f"🔍 **Desglose por Usuario:**\n"
            f"{detalle_usuarios}\n"
            f"✨ *Métricas globales del sistema.*"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as err:
        logger.error(f"Error al obtener métricas: {err}")
        await update.message.reply_text("⚠️ No se pudieron obtener las estadísticas en este momento.")


async def enviar_informe_pdf_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /informe - Genera y envía directamente el PDF de Informe Clínico al chat en el idioma del usuario."""
    user_id = update.effective_user.id
    lang = get_user_language(update, context)
    msg = await update.message.reply_text(t("pdf_generating", lang), parse_mode="Markdown")

    try:
        import pandas as pd
        registros = db.obtener_registros(user_id=user_id)
        if not registros:
            await msg.edit_text(t("pdf_no_data", lang), parse_mode="Markdown")
            return

        df = pd.DataFrame(registros)

        import importlib
        import ai_insights.pdf_generator as pdf_gen_module
        importlib.reload(pdf_gen_module)
        
        pdf_bytes = pdf_gen_module.generar_pdf_clinico(df, lang=lang)
        
        import io
        pdf_file = io.BytesIO(pdf_bytes)
        pdf_file.name = f"Clinical_Report_{datetime.now().strftime('%Y_%m_%d')}.pdf" if lang != "es" else f"Informe_Clinico_Bienestar_{datetime.now().strftime('%Y_%m_%d')}.pdf"

        await update.message.reply_document(
            document=pdf_file,
            filename=pdf_file.name,
            caption=t("pdf_caption", lang),
            parse_mode="Markdown"
        )
        await msg.delete()
    except Exception as err:
        logger.error(f"Error al enviar PDF en /informe: {err}")
        await msg.edit_text(f"⚠️ Ocurrió un inconveniente al generar el PDF: `{err}`", parse_mode="Markdown")


async def idioma_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /idioma /language - Permite cambiar manualmente el idioma del bot."""
    lang = get_user_language(update, context)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇪🇸 Español", callback_data="set_lang_es"), InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en")],
        [InlineKeyboardButton("🇫🇷 Français", callback_data="set_lang_fr")]
    ])
    await update.message.reply_text(t("lang_select_title", lang), parse_mode="Markdown", reply_markup=keyboard)


async def idioma_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Procesa el botón pulsado en la selección de idioma y actualiza los comandos del menú flotante para el usuario."""
    query = update.callback_query
    await query.answer()
    if query.data.startswith("set_lang_"):
        new_lang = query.data.replace("set_lang_", "")
        context.user_data["lang"] = new_lang

        # Actualizar los comandos del menú azul de Telegram para este usuario/chat en tiempo real
        try:
            from telegram import BotCommandScopeChat
            chat_id = update.effective_chat.id
            target_cmds = COMMANDS_BY_LANG.get(new_lang, COMMANDS_BY_LANG["es"])
            await context.bot.set_my_commands(target_cmds, scope=BotCommandScopeChat(chat_id=chat_id))
        except Exception as err:
            logger.error(f"Error actualizando menú de comandos para chat {update.effective_chat.id}: {err}")

        await query.edit_message_text(t("lang_changed", new_lang), parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /ayuda - Muestra los comandos disponibles traducidos al idioma del usuario."""
    lang = get_user_language(update, context)
    await update.message.reply_text(t("help_text", lang), parse_mode="Markdown")


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Comando /cancelar - Cancela la conversación activa."""
    lang = get_user_language(update, context)
    context.user_data.clear()
    context.user_data["lang"] = lang
    await update.message.reply_text(
        t("cancel_msg", lang),
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


# ==============================================================================
async def energia_step(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Procesa la respuesta de ENERGÍA (vía botón en línea o mensaje de texto)."""
    val = None
    if update.callback_query:
        await update.callback_query.answer()
        data = update.callback_query.data
        if data.startswith("energia_"):
            val = int(data.split("_")[1])
    elif update.message and update.message.text:
        text = update.message.text.strip()
        if text.isdigit():
            val = int(text)

    # Validar entrada
    if val is None or not (1 <= val <= 10):
        msg = "⚠️ Por favor, ingresa un número válido entre **1 y 10** para la energía."
        if update.callback_query:
            await update.callback_query.edit_message_text(msg, parse_mode="Markdown", reply_markup=get_rating_keyboard("energia"))
        else:
            await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_rating_keyboard("energia"))
        return ENERGIA

    # Guardar en contexto
    context.user_data["energia"] = val

    humor_text = (
        f"✅ Energía guardada: **{val}/10**\n\n"
        "🎭 **¿Cómo está tu estado de ÁNIMO / HUMOR hoy?** (1 al 10):\n"
        "1 = Muy desanimado/Triste | 10 = Excelente / Súper feliz"
    )

    if update.callback_query:
        await update.callback_query.edit_message_text(
            humor_text,
            parse_mode="Markdown",
            reply_markup=get_rating_keyboard("humor")
        )
    else:
        await update.message.reply_text(
            humor_text,
            parse_mode="Markdown",
            reply_markup=get_rating_keyboard("humor")
        )

    return HUMOR




# ==============================================================================
# AGENTE DE RECORDATORIOS (JobQueue)
# ==============================================================================

def get_horarios_keyboard(lang: str = "es") -> InlineKeyboardMarkup:
    """Genera botones interactivos con opciones comunes de horario diario en el idioma del usuario."""
    labels = {
        "es": ("🌅 Mañana (09:00)", "☀️ Tarde (14:00)", "🌆 Noche (20:00)", "🌙 Antes de dormir (22:00)"),
        "en": ("🌅 Morning (09:00)", "☀️ Afternoon (14:00)", "🌆 Evening (20:00)", "🌙 Before sleep (22:00)"),
        "fr": ("🌅 Matin (09:00)", "☀️ Après-midi (14:00)", "🌆 Soir (20:00)", "🌙 Avant de dormir (22:00)")
    }
    l = labels.get(lang, labels["es"])
    keyboard = [
        [InlineKeyboardButton(l[0], callback_data="set_hora_09:00"), InlineKeyboardButton(l[1], callback_data="set_hora_14:00")],
        [InlineKeyboardButton(l[2], callback_data="set_hora_20:00"), InlineKeyboardButton(l[3], callback_data="set_hora_22:00")]
    ]
    return InlineKeyboardMarkup(keyboard)


async def enviar_recordatorio_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Tarea programada que envía el recordatorio diario y comprueba inactividad de 3 días para alertar compasivamente a la red de apoyo."""
    job = context.job
    chat_id = job.chat_id
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    # Intentar obtener idioma preferido del usuario (de job.data o context.user_data)
    lang = "es"
    if isinstance(job.data, dict) and "lang" in job.data:
        lang = job.data["lang"]
    elif context.user_data and "user_lang" in context.user_data:
        lang = context.user_data["user_lang"]

    btn = InlineKeyboardMarkup([[InlineKeyboardButton(t("btn_register_now", lang), callback_data="iniciar_registro_ahora")]])
    await context.bot.send_message(
        chat_id=chat_id,
        text=t("reminder_msg", lang),
        parse_mode="Markdown",
        reply_markup=btn
    )

    # Comprobar inactividad de 3 días consecutivos
    try:
        import pandas as pd
        registros = db.obtener_registros(user_id=chat_id)
        if registros:
            df = pd.DataFrame(registros)
            if "fecha" in df.columns:
                df["fecha_dt"] = pd.to_datetime(df["fecha"])
                ultima_fecha = df["fecha_dt"].max()
                dias_inactivo = (pd.Timestamp.now().normalize() - ultima_fecha.normalize()).days

                if dias_inactivo >= 3:
                    contactos = db.obtener_contactos_emergencia(chat_id)
                    if contactos:
                        user_name = job.data.get("first_name", "tu ser querido") if isinstance(job.data, dict) else "tu ser querido"
                        msg_apoyo = t("rescue_notification", lang, dias=dias_inactivo, user_name=user_name)
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text=msg_apoyo,
                            parse_mode="Markdown"
                        )
    except Exception as err:
        logger.error(f"Error al verificar inactividad de 3 días: {err}")


async def resumen_semanal_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /resumen_semanal - Muestra el digest motivacional de los últimos 7 días."""
    user_id = update.effective_user.id
    lang = get_user_language(update, context)
    import pandas as pd
    registros = db.obtener_registros(user_id=user_id)

    if not registros:
        await update.message.reply_text(t("weekly_no_data", lang), parse_mode="Markdown")
        return

    df = pd.DataFrame(registros)

    # Filtrar últimos 7 días
    df['fecha'] = pd.to_datetime(df['fecha'])
    hace_semana = pd.Timestamp.now() - pd.Timedelta(days=7)
    df_7d = df[df['fecha'] >= hace_semana]

    if df_7d.empty:
        df_7d = df.tail(7)

    total_registros = len(df_7d)
    avg_energia = df_7d['energia'].mean()
    avg_humor = df_7d['humor'].mean()
    avg_sueno = df_7d['sueno_horas'].mean()

    msg = t("weekly_digest_title", lang, days=total_registros, energia=avg_energia, humor=avg_humor, sueno=avg_sueno)
    await update.message.reply_text(msg, parse_mode="Markdown")


async def set_recordatorio_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Permite elegir interactivamente la hora del recordatorio o enviarla por texto."""
    chat_id = update.effective_chat.id

    lang = get_user_language(update, context)
    # Si pasa un argumento directamente (ej: /recordatorio 21:30)
    if context.args:
        try:
            hora_str = context.args[0]
            time_obj = datetime.strptime(hora_str, "%H:%M").time()

            try:
                import zoneinfo
                tz = zoneinfo.ZoneInfo("Europe/Madrid")
            except Exception:
                import pytz
                tz = pytz.timezone("Europe/Madrid")

            current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
            for job in current_jobs:
                job.schedule_removal()

            context.job_queue.run_daily(
                enviar_recordatorio_job,
                time=time_obj.replace(tzinfo=tz),
                chat_id=chat_id,
                name=str(chat_id),
                data={"lang": lang}
            )

            # Persistir configuración en Supabase
            db.guardar_recordatorio_config(user_id=chat_id, hora=hora_str)

            await update.message.reply_text(
                t("reminder_configured", lang).format(hora=f"{hora_str}hs"),
                parse_mode="Markdown"
            )
            return
        except ValueError:
            pass

    # Si no especifica hora, ofrecer botones para elegir fácilmente
    await update.message.reply_text(
        t("reminder_config_title", lang),
        parse_mode="Markdown",
        reply_markup=get_horarios_keyboard(lang)
    )


async def horario_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja el clic en los botones de selección de horario."""
    query = update.callback_query
    await query.answer()

    lang = get_user_language(update, context)

    if query.data.startswith("set_hora_"):
        hora_str = query.data.replace("set_hora_", "")
        chat_id = update.effective_chat.id
        time_obj = datetime.strptime(hora_str, "%H:%M").time()
        
        # Asignar zona horaria (Europe/Madrid por defecto o UTC)
        try:
            import zoneinfo
            tz = zoneinfo.ZoneInfo("Europe/Madrid")
        except Exception:
            import pytz
            tz = pytz.timezone("Europe/Madrid")

        # Eliminar jobs previos
        current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
        for job in current_jobs:
            job.schedule_removal()

        # Programar nuevo recordatorio diario ajustado a la zona horaria
        context.job_queue.run_daily(
            enviar_recordatorio_job,
            time=time_obj.replace(tzinfo=tz),
            chat_id=chat_id,
            name=str(chat_id),
            data={"lang": lang}
        )

        # Persistir configuración en Supabase
        db.guardar_recordatorio_config(user_id=chat_id, hora=hora_str)

        await query.edit_message_text(
            t("reminder_configured", lang).format(hora=f"{hora_str}hs"),
            parse_mode="Markdown"
        )
    elif query.data == "iniciar_registro_ahora":
        await query.message.reply_text(
            "⚡ **Registro Diario**\n\n"
            "**¿Cómo está tu nivel de ENERGÍA hoy?** (1 al 10):\n"
            "1 = Exhausto | 10 = Plena energía",
            parse_mode="Markdown",
            reply_markup=get_rating_keyboard("energia")
        )


async def remove_recordatorio_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = get_user_language(update, context)
    chat_id = update.effective_chat.id
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    for job in current_jobs:
        job.schedule_removal()
    db.eliminar_recordatorio_config(user_id=chat_id)
    await update.message.reply_text(t("reminder_disabled", lang))


async def test_recordatorio_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envía un recordatorio de prueba programado en 5 segundos."""
    if not context.job_queue:
        await update.message.reply_text(
            "⚠️ **JobQueue no está disponible.**\n"
            "Por favor, instala `APScheduler`: `pip install python-telegram-bot[job-queue]` para activar recordatorios programados.",
            parse_mode="Markdown"
        )
        return

    chat_id = update.effective_chat.id
    context.job_queue.run_once(
        enviar_recordatorio_job,
        when=5,
        chat_id=chat_id,
        name=f"test_{chat_id}"
    )
    await update.message.reply_text("⏱️ **Recordatorio de prueba programado.** Te llegará un mensaje en 5 segundos.", parse_mode="Markdown")


# ==============================================================================
# INICIALIZACIÓN DEL BOT
# ==============================================================================

async def setup_bot_commands(app) -> None:
    """Configura los comandos visibles en el botón azul de Menú de Telegram."""
COMMANDS_BY_LANG = {
    "es": [
        BotCommand("registrar", "⚡ Iniciar check-in diario de bienestar"),
        BotCommand("informe", "📄 Descargar Informe Clínico en PDF"),
        BotCommand("resumen_semanal", "🌸 Ver promedios de la semana"),
        BotCommand("dashboard", "📊 Abrir Panel con gráficos completos"),
        BotCommand("calma", "💙 Espacio de relax y Red de Apoyo"),
        BotCommand("contacto", "🤝 Agregar persona de confianza"),
        BotCommand("recordatorio", "⏰ Configurar hora de notificación"),
        BotCommand("idioma", "🌐 Cambiar idioma / Language"),
        BotCommand("ayuda", "❓ Ver guía de ayuda y comandos")
    ],
    "en": [
        BotCommand("log", "⚡ Start daily wellness check-in"),
        BotCommand("report", "📄 Download Clinical PDF Report"),
        BotCommand("weekly_summary", "🌸 View weekly averages"),
        BotCommand("dashboard", "📊 Open Dashboard with full charts"),
        BotCommand("calm", "💙 Relaxation space & Support Network"),
        BotCommand("contact", "🤝 Add trusted contact"),
        BotCommand("reminder", "⏰ Set daily notification time"),
        BotCommand("language", "🌐 Change language / Idioma"),
        BotCommand("help", "❓ View help guide and commands")
    ],
    "fr": [
        BotCommand("enregistrer", "⚡ Commencer le suivi quotidien de bien-être"),
        BotCommand("rapport", "📄 Télécharger le rapport clinique PDF"),
        BotCommand("resume_hebdo", "🌸 Voir les moyennes de la semaine"),
        BotCommand("dashboard", "📊 Ouvrir le tableau de bord avec graphiques"),
        BotCommand("calme", "💙 Espace relaxation & Réseau de soutien"),
        BotCommand("contact", "🤝 Ajouter un contact de confiance"),
        BotCommand("rappel", "⏰ Configurer l'heure de notification"),
        BotCommand("langue", "🌐 Changer de langue / Language"),
        BotCommand("aide", "❓ Voir le guide d'aide et les commandes")
    ]
}


async def setup_bot_commands(app) -> None:
    """Configura los comandos visibles en el menú flotante y el mensaje de presentación/descripción antes de pulsar Start para ES, EN y FR."""
    try:
        # Comandos del menú
        await app.bot.set_my_commands(COMMANDS_BY_LANG["es"])
        await app.bot.set_my_commands(COMMANDS_BY_LANG["es"], language_code="es")
        await app.bot.set_my_commands(COMMANDS_BY_LANG["en"], language_code="en")
        await app.bot.set_my_commands(COMMANDS_BY_LANG["fr"], language_code="fr")
    except Exception as e:
        logger.warning(f"No se pudieron sincronizar los comandos en Telegram: {e}")

    try:
        # Mensaje de descripción corta
        await app.bot.set_my_short_description("Asistente personal de seguimiento psicoafectivo y bienestar diario. 🌸", language_code="es")
        await app.bot.set_my_short_description("Personal psychoaffective wellness & daily check-in assistant. 🌸", language_code="en")
        await app.bot.set_my_short_description("Assistant personnel de suivi psycho-affectif et bien-être quotidien. 🌸", language_code="fr")
    except Exception as e:
        logger.warning(f"No se pudieron sincronizar las descripciones cortas en Telegram: {e}")

    try:
        # Mensaje de presentación / pantalla de inicio (Aparece en el chat de Telegram antes de pulsar Iniciar / /start)
        desc_es = (
            "✨ ¡Hola! Bienvenido/a a Bot-Bip 💖\n\n"
            "Tu espacio seguro para registrar tu estabilidad, ánimo y descanso.\n\n"
            "🛡️ Comandos clave:\n"
            "• /calma - Ejercicios & Red de Apoyo (llamadas/mensajes)\n"
            "• /contacto - Añadir personas de confianza\n"
            "• /recordatorio - Configurar la hora de tu aviso diario\n"
            "• /dashboard - Panel de gráficos e informes privado"
        )
        desc_en = (
            "✨ Hello! Welcome to Bot-Bip 💖\n\n"
            "Your safe space to log your daily stability, mood, and sleep.\n\n"
            "🛡️ Key commands:\n"
            "• /calm - Exercises & Support Network (calls/messages)\n"
            "• /contact - Add trusted people\n"
            "• /reminder - Set daily notification time\n"
            "• /dashboard - Private charts & report dashboard"
        )
        desc_fr = (
            "✨ Bonjour ! Bienvenue sur Bot-Bip 💖\n\n"
            "Votre espace sécurisé pour suivre votre stabilité, humeur et sommeil.\n\n"
            "🛡️ Commandes clés :\n"
            "• /calme - Exercices & Réseau de soutien (appels/messages)\n"
            "• /contact - Ajouter des personnes de confiance\n"
            "• /rappel - Configurer l'heure de rappel quotidien\n"
            "• /dashboard - Tableau de bord privé & rapports"
        )

        await app.bot.set_my_description(desc_es)
        await app.bot.set_my_description(desc_es, language_code="es")
        await app.bot.set_my_description(desc_en, language_code="en")
        await app.bot.set_my_description(desc_fr, language_code="fr")
    except Exception as e:
        logger.warning(f"No se pudieron sincronizar las descripciones principales en Telegram: {e}")

    # Restaurar alarmas activas desde Supabase al iniciar el bot
    try:
        if app.job_queue:
            recordatorios = db.obtener_todos_recordatorios_activos()
            restaurados = 0
            
            try:
                import zoneinfo
                tz = zoneinfo.ZoneInfo("Europe/Madrid")
            except Exception:
                import pytz
                tz = pytz.timezone("Europe/Madrid")

            for r in recordatorios:
                chat_id = r.get("user_id")
                hora_str = r.get("hora")
                if chat_id and hora_str:
                    try:
                        time_obj = datetime.strptime(hora_str, "%H:%M").time()
                        
                        # Limpiar previas si existieran
                        current_jobs = app.job_queue.get_jobs_by_name(str(chat_id))
                        for job in current_jobs:
                            job.schedule_removal()

                        app.job_queue.run_daily(
                            enviar_recordatorio_job,
                            time=time_obj.replace(tzinfo=tz),
                            chat_id=chat_id,
                            name=str(chat_id)
                        )
                        restaurados += 1
                    except Exception as err_job:
                        logger.error(f"Error restaurando recordatorio para {chat_id}: {err_job}")

            logger.info(f"⏰ Se restauraron {restaurados} recordatorios diarios activos desde Supabase.")
    except Exception as e:
        logger.error(f"Error al restaurar los recordatorios guardados: {e}")


def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN no está definido en las variables de entorno.")
        print("Error: Define TELEGRAM_BOT_TOKEN en tu archivo .env para iniciar el bot.")
        return

    app = ApplicationBuilder().token(token).post_init(setup_bot_commands).build()

    # Configuración del ConversationHandler con comandos traducidos (ES / EN / FR)
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler(["start", "inicio"], start_command),
            CommandHandler(["registrar", "log", "enregistrer"], registrar_command),
            CallbackQueryHandler(registrar_command, pattern="^iniciar_registro_ahora$")
        ],
        per_chat=True,
        per_user=True,
        per_message=False,
        states={
            ENERGIA: [
                CallbackQueryHandler(energia_step, pattern="^energia_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, energia_step)
            ],
            HUMOR: [
                CallbackQueryHandler(humor_step, pattern="^humor_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, humor_step)
            ],
            SUENO: [
                CallbackQueryHandler(sueno_step, pattern="^sueno_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, sueno_step)
            ],
            MEDICACION: [
                CallbackQueryHandler(medicacion_step, pattern="^med_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, medicacion_step)
            ],
            COMENTARIOS: [
                CallbackQueryHandler(comentarios_step, pattern="^skip_comments$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, comentarios_step)
            ]
        },
        fallbacks=[CommandHandler(["cancelar", "cancel", "annuler"], cancel_command)]
    )

    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(horario_callback_handler, pattern="^set_hora_"))
    app.add_handler(CommandHandler(["dashboard", "tableaudebord"], dashboard_command))
    app.add_handler(CommandHandler(["informe", "report", "rapport"], enviar_informe_pdf_command))
    app.add_handler(CommandHandler(["calma", "calm", "calme"], calma_command))
    app.add_handler(CommandHandler(["contacto", "contact"], contacto_command))
    app.add_handler(CommandHandler(["ayuda", "help", "aide"], help_command))
    app.add_handler(CommandHandler(["recordatorio", "reminder", "rappel"], set_recordatorio_command))
    app.add_handler(CommandHandler("recordatorio_off", remove_recordatorio_command))
    app.add_handler(CommandHandler(["resumen_semanal", "weekly_summary", "resume_hebdo"], resumen_semanal_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("test_recordatorio", test_recordatorio_command))
    app.add_handler(CommandHandler(["idioma", "language", "langue"], idioma_command))
    app.add_handler(CallbackQueryHandler(idioma_callback_handler, pattern="^set_lang_"))

    logger.info("Bot-Bip iniciando en modo Polling...")
    app.run_polling()


if __name__ == "__main__":
    main()
