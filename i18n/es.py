# Textos del sistema en Español (ES)

STRINGS = {
    # Comandos /start y Bienvenida
    "welcome_start": "🌸 **¡Hola! Bienvenido/a a Bot-Bip.**\n\nTu asistente personal de bienestar psicoafectivo. Estoy aquí para acompañarte de forma sencilla y sin presiones a registrar tu energía, ánimo, descanso y medicación diaria.\n\nUsa `/registrar` para tu primer check-in o `/ayuda` para ver todos los comandos.",
    "btn_register_now": "📝 Realizar Registro Ahora",
    
    # Flujo de Registro
    "energy_title": "⚡ **Registro Diario de Bienestar**\n\n**¿Cómo está tu nivel de ENERGÍA hoy?** (1 al 10):\n*(1 = Exhausto/a | 10 = Plena energía)*",
    "energy_saved": "✅ Energía guardada: **{val}/10**",
    "humor_title": "🎭 **¿Cómo está tu estado de ÁNIMO / HUMOR hoy?** (1 al 10):\n*(1 = Muy desanimado/Triste | 10 = Excelente / Súper feliz)*",
    "humor_saved": "✅ Estado de ánimo guardado: **{val}/10**",
    "sleep_title": "💤 **¿Cuántas horas has descansado / dormido anoche?**\n*(Selecciona una opción o escribe el número exacto, ej: 7.5)*",
    "sleep_saved": "✅ Descanso guardado: **{val} horas**",
    "medication_title": "💊 **Adherencia a la Medicación:**\n¿Has tomado tu tratamiento prescrito el día de hoy?",
    "medication_saved": "✅ Medicación guardada: **{val}**",
    "comments_title": "📝 **¿Quieres agregar algún comentario u observación?**\n*(Ej: 'Día estresante en el trabajo', 'Paseo por el parque', o presiona Omitir)*",
    "btn_skip": "⏭️ Omitir",
    "record_completed": "✨ **¡Registro Diario Completado!** 🎉\n\nGracias por dedicar este momento a tu autocuidado. Tus datos se han guardado de forma segura.\n\nPuedes consultar tu evolución con `/resumen_semanal` o descargar tu informe médico en PDF con `/informe`.",

    # Teclados de Medicación
    "med_si": "✅ Sí, tomada",
    "med_parcial": "⚠️ Parcial",
    "med_no": "❌ No tomada",
    "med_skip": "⏭️ Omitir / No aplica",

    # Comandos auxiliares
    "calma_title": "💙 **Espacio de Calma & Red de Apoyo** 🌿\n\nTómate un momento. Estás a salvo. Vamos a conectar con el presente:\n\n🌬️ **Técnica 4-7-8 de Respiración:**\n1. Inhala por la nariz contando hasta **4**.\n2. Mantén el aire contando hasta **7**.\n3. Exhala despacio por la boca contando hasta **8**.\n\n👁️ **Técnica 5-4-3-2-1 de Anclaje:**\n• Nombra **5 cosas** que veas a tu alrededor.\n• Nombra **4 cosas** que puedas tocar.\n• Nombra **3 sonidos** que escuches.\n• Nombra **2 olores** que percibas.\n• Nombra **1 emoción** que sientas sin juzgarla.\n\n💊 *Recordatorio amable: ¿Has tomado tu medicación habitual de hoy?*",
    "calma_contact_tip": "\n\n💡 *Tip: Puedes agregar tus contactos de confianza enviando:* `/contacto Nombre Telefono` (ej: `/contacto Gabriel +34600000000`)",
    "calma_contacts_header": "\n\n🤝 **Tu Red de Apoyo de Confianza:**\n",
    "calma_btn_msg": "💬 Mensaje a {nombre}",

    # Contacto
    "contacto_usage": "⚠️ **Uso correcto:** `/contacto Nombre Telefono [Relacion]`\nEjemplo: `/contacto Gabriel +34600000000 Pareja`",
    "contacto_saved": "✅ **Contacto guardado con éxito:**\n• **Nombre:** {nombre}\n• **Teléfono:** {telefono}\n• **Relación:** {relacion}",

    # Recordatorio e Inactividad
    "reminder_msg": "🔔 **¡Hola! Es momento de tu check-in diario de bienestar.**\n\nPresiona el botón de abajo o envía /registrar para responder tus preguntas rápidas.",
    "rescue_notification": "💙 **Notificación de Acompañamiento y Rescate:**\n\nHola, notamos que han pasado {dias} días sin registros de bienestar de {user_name}.\nEn momentos de cansancio o bajón, es totalmente normal hacer una pausa. Podría ser un buen momento para enviarle un mensaje cariñoso, una llamada o un abrazo sin presiones. 🌸",
    "reminder_config_title": "⏰ **Configuración de Recordatorio Diario**\n\nSelecciona el horario en el que prefieres recibir tu notificación diaria:",
    "reminder_configured": "✅ **¡Excelente! Recordatorio configurado.**\n\nTe enviaré una notificación diaria automática a las **{hora}hs** para realizar tu check-in.\n*(Puedes cambiar la hora cuando quieras con /recordatorio)*",

    # Resumen Semanal
    "weekly_no_data": "🌸 **Aviso:** No hay suficientes registros guardados esta semana. ¡Comienza hoy con `/registrar`!",
    "weekly_digest_title": "🌸 **Tu Digest Semanal de Bienestar** 📊\n\n🗓️ **Días registrados esta semana:** {days}/7 días\n⚡ **Promedio Energía:** {energia:.1f}/10\n🎭 **Promedio Ánimo:** {humor:.1f}/10\n💤 **Promedio Descanso:** {sueno:.1f}h/noche\n\n✨ *¡Gran trabajo manteniendo la constancia de tus rutinas! Recuerda que puedes descargar tu informe en PDF con /informe.*",

    # PDF Clínico
    "pdf_generating": "📄 **Generando tu Informe Clínico PDF...** Un momento por favor...",
    "pdf_no_data": "🌸 **Aviso:** No se encontraron registros de bienestar guardados aún. Inicia con `/registrar`.",
    "pdf_caption": "📄 **Aquí tienes tu Informe Clínico en PDF** listo para tu consulta médica o guardar en tus archivos.",
    "pdf_col_date": "Fecha",
    "pdf_col_energy": "Energia",
    "pdf_col_mood": "Animo",
    "pdf_col_sleep": "Sueño (h)",
    "pdf_col_medication": "Medicacion",
    "pdf_col_notes": "Notas / Observaciones",
    "pdf_report_title": "INFORME CLINICO DE BIENESTAR Y ESTABILIDAD",
    "pdf_report_subtitle": "Seguimiento psicoafectivo de energia, estado de animo y descanso",

    # Selección de Idioma
    "lang_select_title": "🌐 **Selección de Idioma / Language Selection / Sélection de la langue**\n\nPor favor, elige tu idioma preferido:",
    "lang_changed": "✅ **Idioma cambiado a Español correctamente.**",
    
    # Ayuda
    "help_text": "🤖 **Bot-Bip - Comandos de Apoyo & Registro**\n\n• `/registrar` - Check-in diario (Energía, Ánimo, Sueño y Medicación).\n• `/informe` - Recibir tu **Informe Clínico PDF** directo en el chat.\n• `/resumen_semanal` - Ver tu promedios de estabilidad de los últimos 7 días.\n• `/dashboard` - Abrir tu panel de gráficos completos en el navegador.\n• `/calma` - Espacio de relajación y botones de llamada/mensaje a tu **Red de Apoyo**.\n• `/contacto` - Agregar personas de confianza.\n• `/recordatorio` - Configurar la hora de tu notificación diaria.\n• `/idioma` - Cambiar idioma (Español, English, Français).\n• `/cancelar` - Cancelar el registro en curso.\n• `/ayuda` - Ver este mensaje de ayuda."
}
