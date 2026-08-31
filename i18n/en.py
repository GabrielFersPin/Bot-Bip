# Textos del sistema en Inglés (EN)

STRINGS = {
    # Start & Welcome
    "welcome_start": "🌸 **Hello! Welcome to Bot-Bip.**\n\nYour personal psychoaffective wellness companion. I am here to help you effortlessly log your energy, mood, sleep, and daily medication without any pressure.\n\nUse `/registrar` for your first check-in or `/ayuda` to view all commands.",
    "btn_register_now": "📝 Check-in Now",
    
    # Check-in Flow
    "energy_title": "⚡ **Daily Wellness Check-in**\n\n**How is your ENERGY level today?** (1 to 10):\n*(1 = Exhausted | 10 = Full Energy)*",
    "energy_saved": "✅ Energy saved: **{val}/10**",
    "humor_title": "🎭 **How is your MOOD today?** (1 to 10):\n*(1 = Very Low/Sad | 10 = Excellent / Super Happy)*",
    "humor_saved": "✅ Mood saved: **{val}/10**",
    "sleep_title": "💤 **How many hours of SLEEP / rest did you get last night?**\n*(Select an option or type the exact number, e.g., 7.5)*",
    "sleep_saved": "✅ Sleep saved: **{val} hours**",
    "medication_title": "💊 **Medication Adherence:**\nDid you take your prescribed treatment today?",
    "medication_saved": "✅ Medication status saved: **{val}**",
    "comments_title": "📝 **Would you like to add any notes or observations?**\n*(E.g., 'Stressful day at work', 'Walk in the park', or tap Skip)*",
    "btn_skip": "⏭️ Skip",
    "record_completed": "✨ **Daily Check-in Completed!** 🎉\n\nThank you for taking this moment for self-care. Your data has been securely saved.\n\nYou can check your progress with `/resumen_semanal` or download your clinical PDF report with `/informe`.",

    # Medication Keyboards
    "med_si": "✅ Yes, taken",
    "med_parcial": "⚠️ Partial",
    "med_no": "❌ Not taken",
    "med_skip": "⏭️ Skip / Not applicable",

    # Calm & Support
    "calma_title": "💙 **Calm Space & Support Network** 🌿\n\nTake a moment. You are safe. Let's connect with the present moment:\n\n🌬️ **4-7-8 Breathing Technique:**\n1. Inhale through your nose for **4** seconds.\n2. Hold your breath for **7** seconds.\n3. Exhale slowly through your mouth for **8** seconds.\n\n👁️ **5-4-3-2-1 Grounding Technique:**\n• Name **5 things** you can see around you.\n• Name **4 things** you can touch.\n• Name **3 sounds** you can hear.\n• Name **2 smells** you can perceive.\n• Name **1 emotion** you feel without judgment.\n\n💊 *Gentle reminder: Have you taken your daily medication today?*",
    "calma_contact_tip": "\n\n💡 *Tip: You can add trusted contacts by sending:* `/contacto Name Phone` (e.g., `/contacto Gabriel +34600000000`)",
    "calma_contacts_header": "\n\n🤝 **Your Trusted Support Network:**\n",
    "calma_btn_msg": "💬 Message {nombre}",

    # Contact
    "contacto_usage": "⚠️ **Correct usage:** `/contacto Name Phone [Relationship]`\nExample: `/contacto Gabriel +34600000000 Partner`",
    "contacto_saved": "✅ **Contact saved successfully:**\n• **Name:** {nombre}\n• **Phone:** {telefono}\n• **Relationship:** {relacion}",

    # Reminder & Rescue
    "reminder_msg": "🔔 **Hello! It's time for your daily wellness check-in.**\n\nTap the button below or send /registrar to answer your quick questions.",
    "rescue_notification": "💙 **Support & Care Notification:**\n\nHello, we noticed it has been {dias} days without wellness logs from {user_name}.\nDuring low or exhausting times, taking a pause is completely normal. It might be a great moment to send a warm message, call, or hug without any pressure. 🌸",
    "reminder_config_title": "⏰ **Daily Reminder Configuration**\n\nSelect the time you prefer to receive your daily notification:",
    "reminder_configured": "✅ **Great! Reminder set.**\n\nI will send you an automatic daily notification at **{hora}** for your check-in.\n*(You can change the time whenever you want with /recordatorio)*",

    # Weekly Digest
    "weekly_no_data": "🌸 **Notice:** Not enough entries saved this week. Start today with `/registrar`!",
    "weekly_digest_title": "🌸 **Your Weekly Wellness Digest** 📊\n\n🗓️ **Days logged this week:** {days}/7 days\n⚡ **Average Energy:** {energia:.1f}/10\n🎭 **Average Mood:** {humor:.1f}/10\n💤 **Average Sleep:** {sueno:.1f}h/night\n\n✨ *Great job staying consistent! Remember you can download your clinical PDF report with /informe.*",

    # Clinical PDF
    "pdf_generating": "📄 **Generating your Clinical PDF Report...** One moment please...",
    "pdf_no_data": "🌸 **Notice:** No wellness logs found yet. Start logging with `/registrar`.",
    "pdf_caption": "📄 **Here is your Clinical PDF Report** ready to present at your doctor appointment or keep in your records.",
    "pdf_col_date": "Date",
    "pdf_col_energy": "Energy",
    "pdf_col_mood": "Mood",
    "pdf_col_sleep": "Sleep (h)",
    "pdf_col_medication": "Medication",
    "pdf_col_notes": "Notes / Observations",
    "pdf_report_title": "WELLNESS AND STABILITY CLINICAL REPORT",
    "pdf_report_subtitle": "Psychoaffective monitoring of energy, mood, and sleep rest",

    # Language Selection
    "lang_select_title": "🌐 **Language Selection / Selección de Idioma / Sélection de la langue**\n\nPlease select your preferred language:",
    "lang_changed": "✅ **Language changed to English successfully.**",

    # Dashboard
    "dashboard_btn": "📊 Open My Wellness Dashboard",
    "dashboard_msg": "✨ **Your Private Wellness Dashboard**\n\nTap the button below to view your stability charts, consult your AI wellness assistant, and download your clinical PDF report for doctor appointments:",

    # Cancel & Reminder Off
    "cancel_msg": "❌ Check-in canceled. You can start again whenever you want using /registrar.",
    "reminder_disabled": "🔕 Daily reminder turned off.",

    # Help
    "help_text": "🤖 **Bot-Bip - Support & Check-in Commands**\n\n• `/registrar` - Daily check-in (Energy, Mood, Sleep & Medication).\n• `/informe` - Receive your **Clinical PDF Report** directly in chat.\n• `/resumen_semanal` - View your 7-day stability averages.\n• `/dashboard` - Open your full browser interactive dashboard.\n• `/calma` - Relaxation space and quick call/message buttons for your **Support Network**.\n• `/contacto` - Add a trusted contact person.\n• `/recordatorio` - Set your daily notification time.\n• `/idioma` - Change language (Spanish, English, French).\n• `/cancelar` - Cancel the current check-in.\n• `/ayuda` - Show this help message."
}
