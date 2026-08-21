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
ENERGIA, HUMOR, COMENTARIOS = range(3)

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
    """Comando /start - Da la bienvenida e inicia el registro diario."""
    user = update.effective_user
    welcome_text = (
        f"👋 ¡Hola, {user.first_name}!\n\n"
        "Soy **Bot-Bip**, tu agente personal para registrar tu nivel diario de energía, humor y observaciones.\n\n"
        "Comenzemos con el registro de hoy. ⚡\n"
        "**¿Cómo está tu nivel de ENERGÍA hoy?** (Selecciona o escribe un número del 1 al 10):\n"
        "1 = Exhausto / Sin energía | 10 = Máxima energía / Imparable"
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
        "⚡ **Registro Diario**\n\n"
        "**¿Cómo está tu nivel de ENERGÍA hoy?** (1 al 10):\n"
        "1 = Exhausto | 10 = Plena energía"
    )
    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_rating_keyboard("energia")
    )
    return ENERGIA


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /ayuda - Muestra los comandos disponibles."""
    help_text = (
        "🤖 **Bot-Bip - Comandos Disponibles**\n\n"
        "• `/registrar` - Iniciar el registro diario de energía y humor.\n"
        "• `/recordatorio HH:MM` - Configurar recordatorio diario (ej: `/recordatorio 21:00`).\n"
        "• `/recordatorio_off` - Desactivar el recordatorio diario.\n"
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
# PASOS DE LA CONVERSACIÓN Y VALIDACIÓN
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


async def humor_step(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Procesa la respuesta de HUMOR (vía botón en línea o mensaje de texto)."""
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

    # Validar entrada
    if val is None or not (1 <= val <= 10):
        msg = "⚠️ Por favor, ingresa un número válido entre **1 y 10** para el humor."
        if update.callback_query:
            await update.callback_query.edit_message_text(msg, parse_mode="Markdown", reply_markup=get_rating_keyboard("humor"))
        else:
            await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_rating_keyboard("humor"))
        return HUMOR

    # Guardar en contexto
    context.user_data["humor"] = val

    comment_text = (
        f"✅ Humor guardado: **{val}/10**\n\n"
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
    """Procesa el comentario final y guarda todo en Supabase."""
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

    # Guardar en Supabase usando el agente de base de datos
    result = db.guardar_registro_diario(
        user_id=user_id,
        energia=energia,
        humor=humor,
        comentarios=comentario
    )

    context.user_data.clear()

    if result.get("success"):
        summary_text = (
            "🎉 **¡Registro Guardado con Éxito!**\n\n"
            f"⚡ **Energía:** {energia}/10\n"
            f"🎭 **Humor:** {humor}/10\n"
            f"📝 **Comentario:** {comentario if comentario else 'Sin comentarios'}\n\n"
            "¡Gracias por registrar tu día! Puedes ver tus estadísticas en el Dashboard."
        )
    else:
        summary_text = (
            "❌ Hubo un inconveniente al guardar tu registro en la base de datos.\n"
            f"Detalle: `{result.get('error')}`"
        )

    if update.callback_query:
        await update.callback_query.edit_message_text(summary_text, parse_mode="Markdown")
    else:
        await update.message.reply_text(summary_text, parse_mode="Markdown")

    return ConversationHandler.END


# ==============================================================================
# AGENTE DE RECORDATORIOS (JobQueue)
# ==============================================================================

async def enviar_recordatorio_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Tarea programada que envía el recordatorio de registro diario."""
    job = context.job
    await context.bot.send_message(
        chat_id=job.chat_id,
        text="🔔 **¡Hola! Hora de registrar tu día.**\n\nUsa /registrar para responder tus preguntas de energía y humor.",
        parse_mode="Markdown"
    )


async def set_recordatorio_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Configura una tarea programada diaria usando JobQueue."""
    chat_id = update.effective_chat.id
    if not context.args:
        await update.message.reply_text(
            "⚠️ Por favor indica la hora en formato HH:MM (24h). Ej: `/recordatorio 20:30`",
            parse_mode="Markdown"
        )
        return

    try:
        hora_str = context.args[0]
        time_obj = datetime.strptime(hora_str, "%H:%M").time()

        # Eliminar jobs previos del mismo chat
        current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
        for job in current_jobs:
            job.schedule_removal()

        # Programar job diario
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
    except ValueError:
        await update.message.reply_text("❌ Formato de hora inválido. Usa HH:MM en 24 horas (ej: 21:00).")


async def remove_recordatorio_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Desactiva el recordatorio diario."""
    chat_id = update.effective_chat.id
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    for job in current_jobs:
        job.schedule_removal()
    await update.message.reply_text("🔕 Recordatorio diario desactivado.")


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
            CommandHandler("registrar", registrar_command)
        ],
        states={
            ENERGIA: [
                CallbackQueryHandler(energia_step, pattern="^energia_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, energia_step)
            ],
            HUMOR: [
                CallbackQueryHandler(humor_step, pattern="^humor_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, humor_step)
            ],
            COMENTARIOS: [
                CallbackQueryHandler(comentarios_step, pattern="^skip_comments$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, comentarios_step)
            ]
        },
        fallbacks=[CommandHandler("cancelar", cancel_command)]
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("ayuda", help_command))
    app.add_handler(CommandHandler("recordatorio", set_recordatorio_command))
    app.add_handler(CommandHandler("recordatorio_off", remove_recordatorio_command))

    logger.info("Bot-Bip iniciando en modo Polling...")
    app.run_polling()


if __name__ == "__main__":
    main()
