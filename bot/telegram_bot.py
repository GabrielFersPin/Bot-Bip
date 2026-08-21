import os
import logging
from datetime import datetime, time
from typing import Dict, Any

from dotenv import load_dotenv
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove
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

# Configuración de Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Estados de la conversación
ENERGIA, HUMOR, SUENO, COMENTARIOS = range(4)

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
    contactos = db.obtener_contactos_emergencia(user_id)

    keyboard = []
    text_contactos = ""

    if contactos:
        text_contactos = "\n\n🤝 **Tu Red de Apoyo de Confianza:**\n"
        for c in contactos:
            nombre = c.get("nombre")
            telefono = c.get("telefono", "").replace(" ", "").replace("-", "")
            relacion = c.get("relacion", "Apoyo")
            text_contactos += f"• **{nombre}** ({relacion}): `{telefono}`\n"
            
            # Usar urllib.parse.quote_plus para que WhatsApp formatee los espacios de manera limpia
            import urllib.parse
            mensaje_apoyo = f"Hola {nombre}, estoy pasando por un momento difícil y necesito apoyo."
            mensaje_encoded = urllib.parse.quote_plus(mensaje_apoyo)
            
            clean_phone = telefono.replace("+", "")
            keyboard.append([
                InlineKeyboardButton(f"💬 Mensaje a {nombre}", url=f"https://wa.me/{clean_phone}?text={mensaje_encoded}")
            ])
    else:
        text_contactos = "\n\n💡 *Tip: Puedes agregar tus contactos de confianza enviando:* `/contacto Nombre Telefono` (ej: `/contacto Gabriel +34600000000`)"

    calma_text = (
        "💙 **Espacio de Calma & Red de Apoyo** 🌿\n\n"
        "Tómate un momento. Estás a salvo. Vamos a conectar con el presente:\n\n"
        "🌬️ **Técnica 4-7-8 de Respiración:**\n"
        "1. Inhala por la nariz contando hasta **4**.\n"
        "2. Mantén el aire contando hasta **7**.\n"
        "3. Exhala despacio por la boca contando hasta **8**.\n\n"
        "👁️ **Técnica 5-4-3-2-1 de Anclaje:**\n"
        "• Nombra **5 cosas** que veas a tu alrededor.\n"
        "• Nombra **4 cosas** que puedas tocar.\n"
        "• Nombra **3 sonidos** que escuches.\n"
        "• Nombra **2 olores** que percibas.\n"
        "• Nombra **1 emoción** que sientas sin juzgarla.\n\n"
        "💊 *Recordatorio amable: ¿Has tomado tu medicación habitual de hoy?*"
        f"{text_contactos}"
    )

    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    await update.message.reply_text(calma_text, parse_mode="Markdown", reply_markup=reply_markup)


async def agregar_contacto_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /contacto - Permite registrar un número de teléfono de la red de apoyo."""
    user_id = update.effective_user.id
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "⚠️ **Formato para agregar contacto:**\n"
            "`/contacto Nombre Telefono [Relacion]`\n\n"
            "Ejemplo:\n`/contacto Gabriel +34600000000 Pareja`\n"
            "`/contacto Dra.Ramos +34611111111 Terapeuta`",
            parse_mode="Markdown"
        )
        return

    nombre = context.args[0]
    telefono = context.args[1]
    relacion = context.args[2] if len(context.args) > 2 else "Red de Apoyo"

    res = db.guardar_contacto_emergencia(user_id=user_id, nombre=nombre, telefono=telefono, relacion=relacion)

    if res.get("success"):
        await update.message.reply_text(
            f"✅ **Contacto añadido a tu Red de Apoyo:**\n"
            f"👤 **Nombre:** {nombre}\n"
            f"📞 **Teléfono:** `{telefono}`\n"
            f"🏷️ **Relación:** {relacion}\n\n"
            "Ahora aparecerá con botones de llamada y mensaje directo al usar `/calma`.",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(f"❌ Error al guardar contacto: `{res.get('error')}`", parse_mode="Markdown")


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

    comment_text = (
        f"✅ Descanso guardado: **{val}h**\n\n"
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

    # Guardar en Supabase
    result = db.guardar_registro_diario(
        user_id=user_id,
        energia=energia,
        humor=humor,
        sueno_horas=sueno_horas,
        comentarios=comentario
    )

    context.user_data.clear()

    # Detección precoz de alertas clínicas (Virajes de fase)
    alerta_text = ""
    if energia >= 9 and sueno_horas <= 4:
        alerta_text = (
            "\n\n⚠️ **Aviso de Bienestar:** Notamos alta energía (9-10) con muy pocas horas de descanso (<4h). "
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
    """Comando /start - Bienvenida concisa e inicio inmediato de registro."""
    user = update.effective_user
    welcome_text = (
        f"✨ **¡Hola, {user.first_name}! Bienvenido/a a Bot-Bip** 💖\n\n"
        "Tu espacio seguro para registrar tu **estabilidad y descanso**.\n\n"
        "🛡️ **Comandos clave:**\n"
        "• `/calma` - Ejercicios & Red de Apoyo (llamadas/mensajes)\n"
        "• `/contacto` - Añadir personas de confianza\n"
        "• `/recordatorio` - Configurar la hora de tu aviso diario\n"
        "• `/dashboard` - Panel de gráficos e informes privados\n\n"
        "⚡ **¿Cómo está tu nivel de ENERGÍA hoy?** (1 al 10):\n"
        "*(1 = Exhausto/a | 10 = Imparable)*"
    )
    await update.message.reply_text(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=get_rating_keyboard("energia")
    )
    return ENERGIA


async def registrar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Comando /registrar - Inicia el flujo de preguntas."""
    text = (
        "⚡ **Registro Diario de Bienestar**\n\n"
        "**¿Cómo está tu nivel de ENERGÍA hoy?** (1 al 10):\n"
        "*(1 = Exhausto/a | 10 = Plena energía)*"
    )
    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_rating_keyboard("energia")
    )
    return ENERGIA


async def dashboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /dashboard - Envia enlace nativo WebApp a Streamlit filtrado por el ID del usuario."""
    user_id = update.effective_user.id
    url_base = os.getenv("DASHBOARD_URL", "http://localhost:8501")
    keyboard = [
        [InlineKeyboardButton("📊 Abrir Mi Resumen de Bienestar", url=url_personalizada)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "✨ **Tu Panel Privado de Bienestar**\n\n"
        "Presiona el botón de abajo para ver tus gráficos de estabilidad, consultar a tu asistente de bienestar y descargar tu informe PDF para la consulta médica:",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /ayuda - Muestra los comandos disponibles."""
    help_text = (
        "🤖 **Bot-Bip - Comandos de Apoyo & Registro**\n\n"
        "• `/registrar` - Iniciar el check-in diario (Energía, Ánimo y Descanso).\n"
        "• `/calma` - Espacio de relajación y botones de llamada/mensaje a tu **Red de Apoyo**.\n"
        "• `/contacto` - Agregar personas de confianza (ej: `/contacto Gabriel +34600000000 Pareja`).\n"
        "• `/recordatorio` - Configurar la hora de tu notificación diaria.\n"
        "• `/dashboard` - Abrir tu panel privado de estadísticas en Telegram.\n"
        "• `/cancelar` - Cancelar el registro actual.\n"
        "• `/ayuda` - Ver este mensaje de ayuda."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Comando /cancelar - Cancela la conversación activa."""
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Registro cancelado. Puedes iniciar de nuevo cuando quieras usando /registrar.",
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

def get_horarios_keyboard() -> InlineKeyboardMarkup:
    """Genera botones interactivos con opciones comunes de horario diario."""
    keyboard = [
        [InlineKeyboardButton("🌅 Mañana (09:00)", callback_data="set_hora_09:00"), InlineKeyboardButton("☀️ Tarde (14:00)", callback_data="set_hora_14:00")],
        [InlineKeyboardButton("🌆 Noche (20:00)", callback_data="set_hora_20:00"), InlineKeyboardButton("🌙 Antes de dormir (22:00)", callback_data="set_hora_22:00")]
    ]
    return InlineKeyboardMarkup(keyboard)


async def enviar_recordatorio_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Tarea programada que envía el recordatorio de registro diario con botón de inicio rápido."""
    job = context.job
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    btn = InlineKeyboardMarkup([[InlineKeyboardButton("📝 Realizar Registro Ahora", callback_data="iniciar_registro_ahora")]])
    await context.bot.send_message(
        chat_id=job.chat_id,
        text="🔔 **¡Hola! Es momento de tu check-in diario de bienestar.**\n\nPresiona el botón de abajo o envía /registrar para responder tus 3 preguntas rápidas.",
        parse_mode="Markdown",
        reply_markup=btn
    )


async def set_recordatorio_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Permite elegir interactivamente la hora del recordatorio o enviarla por texto."""
    chat_id = update.effective_chat.id

    # Si pasa un argumento directamente (ej: /recordatorio 21:30)
    if context.args:
        try:
            hora_str = context.args[0]
            time_obj = datetime.strptime(hora_str, "%H:%M").time()

            current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
            for job in current_jobs:
                job.schedule_removal()

            context.job_queue.run_daily(
                enviar_recordatorio_job,
                time=time_obj,
                chat_id=chat_id,
                name=str(chat_id)
            )

            await update.message.reply_text(
                f"⏰ **Recordatorio programado diariamente a las {hora_str}hs.**",
                parse_mode="Markdown"
            )
            return
        except ValueError:
            pass

    # Si no especifica hora, ofrecer botones para elegir fácilmente
    await update.message.reply_text(
        "⏰ **Configuración de Recordatorio Diario**\n\n"
        "Elige la hora que mejor se adapte a tu rutina para recibir tu notificación diaria automática:\n"
        "*(O escribe `/recordatorio HH:MM` con tu hora personalizada)*",
        parse_mode="Markdown",
        reply_markup=get_horarios_keyboard()
    )


async def horario_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja el clic en los botones de selección de horario."""
    query = update.callback_query
    await query.answer()

    if query.data.startswith("set_hora_"):
        hora_str = query.data.replace("set_hora_", "")
        chat_id = update.effective_chat.id
        time_obj = datetime.strptime(hora_str, "%H:%M").time()

        # Eliminar jobs previos
        current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
        for job in current_jobs:
            job.schedule_removal()

        # Programar nuevo recordatorio diario
        context.job_queue.run_daily(
            enviar_recordatorio_job,
            time=time_obj,
            chat_id=chat_id,
            name=str(chat_id)
        )

        await query.edit_message_text(
            f"✅ **¡Excelente! Recordatorio configurado.**\n\n"
            f"Te enviaré una notificación diaria automática a las **{hora_str}hs** para realizar tu check-in.\n"
            f"*(Puedes cambiar la hora cuando quieras con /recordatorio)*",
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
    await update.message.reply_text("🔕 Recordatorio diario desactivado.")


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
    await update.message.reply_text("⏱️ **Recordatorio de prueba programado.** Te llegará un mensaje en 5 segundos...", parse_mode="Markdown")


# ==============================================================================
# INICIALIZACIÓN DEL BOT
# ==============================================================================

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN no está definido en las variables de entorno.")
        print("Error: Define TELEGRAM_BOT_TOKEN en tu archivo .env para iniciar el bot.")
        return

    app = ApplicationBuilder().token(token).build()

    # Configuración del ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start_command),
            CommandHandler("registrar", registrar_command),
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
            COMENTARIOS: [
                CallbackQueryHandler(comentarios_step, pattern="^skip_comments$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, comentarios_step)
            ]
        },
        fallbacks=[CommandHandler("cancelar", cancel_command)]
    )

    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(horario_callback_handler, pattern="^(set_hora_|iniciar_registro_ahora)"))
    app.add_handler(CommandHandler("dashboard", dashboard_command))
    app.add_handler(CommandHandler("calma", calma_command))
    app.add_handler(CommandHandler("contacto", agregar_contacto_command))
    app.add_handler(CommandHandler("ayuda", help_command))
    app.add_handler(CommandHandler("recordatorio", set_recordatorio_command))
    app.add_handler(CommandHandler("recordatorio_off", remove_recordatorio_command))
    app.add_handler(CommandHandler("test_recordatorio", test_recordatorio_command))

    logger.info("Bot-Bip iniciando en modo Polling...")
    app.run_polling()


if __name__ == "__main__":
    main()
