# Textos del sistema en Francés (FR)

STRINGS = {
    # Start & Welcome
    "welcome_start": "🌸 **Bonjour ! Bienvenue sur Bot-Bip.**\n\nVotre assistant personnel de bien-être psycho-affectif. Je suis là pour vous accompagner simplement et sans pression dans le suivi quotidien de votre énergie, humeur, sommeil et médication.\n\nUtilisez `/enregistrer` (`/registrar`) pour votre premier suivi ou `/aide` (`/ayuda`) pour voir toutes les commandes.",
    "btn_register_now": "📝 Faire le suivi maintenant",
    
    # Check-in Flow
    "energy_title": "⚡ **Suivi Quotidien du Bien-être**\n\n**Quel est votre niveau d'ÉNERGIE aujourd'hui ?** (1 à 10) :\n*(1 = Épuisé(e) | 10 = Pleine énergie)*",
    "energy_saved": "✅ Énergie enregistrée : **{val}/10**",
    "humor_title": "🎭 **Quel est votre état d'HUMEUR aujourd'hui ?** (1 à 10) :\n*(1 = Très bas/Triste | 10 = Excellent / Très heureux)*",
    "humor_saved": "✅ Humeur enregistrée : **{val}/10**",
    "sleep_title": "💤 **Combien d'heures avez-vous DORMI la nuit dernière ?**\n*(Sélectionnez une option ou saisissez le nombre exact, ex : 7.5)*",
    "sleep_saved": "✅ Sommeil enregistré : **{val} heures**",
    "medication_title": "💊 **Observance du traitement :**\nAvez-vous pris votre traitement prescrit aujourd'hui ?",
    "medication_saved": "✅ Statut du traitement enregistré : **{val}**",
    "comments_title": "📝 **Souhaitez-vous ajouter des remarques ou observations ?**\n*(Ex : 'Journée stressante', 'Promenade au parc', ou appuyez sur Ignorer)*",
    "btn_skip": "⏭️ Ignorer",
    "record_completed": "✨ **Suivi quotidien terminé !** 🎉\n\nMerci d'avoir pris ce moment pour prendre soin de vous. Vos données ont été enregistrées en toute sécurité.\n\nVous pouvez consulter votre évolution avec `/resume_hebdo` (`/resumen_semanal`) ou télécharger votre rapport médical en PDF avec `/rapport` (`/informe`).",

    # Medication Keyboards
    "med_si": "✅ Oui, pris",
    "med_parcial": "⚠️ Partiel",
    "med_no": "❌ Non pris",
    "med_skip": "⏭️ Ignorer / Non applicable",

    # Calm & Support
    "calma_title": "💙 **Espace Calme & Réseau de Soutien** 🌿\n\nPrenez un moment. Vous êtes en sécurité. Connectons-nous au moment présent :\n\n🌬️ **Technique de respiration 4-7-8 :**\n1. Inspirez par le nez en comptant jusqu'à **4**.\n2. Retenez votre souffle en comptant jusqu'à **7**.\n3. Expirez lentement par la bouche en comptant jusqu'à **8**.\n\n👁️ **Technique d'ancrage 5-4-3-2-1 :**\n• Nommez **5 choses** que vous voyez autour de vous.\n• Nommez **4 choses** que vous pouvez toucher.\n• Nommez **3 sons** que vous entendez.\n• Nommez **2 odeurs** que vous percevez.\n• Nommez **1 émotion** que vous ressentez sans la juger.\n\n💊 *Rappel bienveillant : Avez-vous pris votre traitement habituel aujourd'hui ?*",
    "calma_contact_tip": "\n\n💡 *Astuce : Vous pouvez ajouter un contact de confiance en envoyant :* `/contacto Nom Telephone` (ex : `/contacto Gabriel +34600000000`)",
    "calma_contacts_header": "\n\n🤝 **Votre réseau de soutien de confiance :**\n",
    "calma_btn_msg": "💬 Envoyer un message à {nombre}",

    # Contact
    "contacto_usage": "⚠️ **Format pour ajouter un contact :**\n`/contact Nom Telephone [Relation]`\n\nExemple :\n`/contact Gabriel +34600000000 Partenaire`\n`/contact Dr.Ramos +34611111111 Thérapeute`",
    "contacto_saved": "✅ **Contact ajouté à votre Réseau de Soutien :**\n👤 **Nom :** {nombre}\n📞 **Téléphone :** `{telefono}`\n🏷️ **Relation :** {relacion}\n\nIl apparaîtra désormais avec des boutons d'appel et de message lors de l'utilisation de `/calme`.",

    # Reminder & Rescue
    "reminder_msg": "🔔 **Bonjour ! C'est l'heure de votre suivi quotidien de bien-être.**\n\nAppuyez sur le bouton ci-dessous ou envoyez /registrar pour répondre aux questions rapides.",
    "rescue_notification": "💙 **Notification d'accompagnement et de soutien :**\n\nBonjour, nous avons remarqué que cela fait {dias} jours sans enregistrement de bien-être de {user_name}.\nDans les moments de fatigue ou de baisse de moral, faire une pause est tout à fait normal. Ce serait peut-être le bon moment pour envoyer un message chaleureux ou passer un appel sans pression. 🌸",
    "reminder_config_title": "⏰ **Configuration du rappel quotidien**\n\nSélectionnez l'heure à laquelle vous préférez recevoir votre notification quotidienne :",
    "reminder_configured": "✅ **Parfait ! Rappel configuré.**\n\nJe vous enverrai une notification quotidienne automatique à **{hora}** pour effectuer votre suivi.\n*(Vous pouvez modifier l'heure à tout moment avec /recordatorio)*",

    # Weekly Digest
    "weekly_no_data": "🌸 **Avis :** Pas assez d'enregistrements cette semaine. Commencez dès aujourd'hui avec `/enregistrer` !",
    "weekly_digest_title": "🌸 **Votre bilan hebdomadaire de bien-être** 📊\n\n🗓️ **Jours enregistrés cette semaine :** {days}/7 jours\n⚡ **Énergie moyenne :** {energia:.1f}/10\n🎭 **Humeur moyenne :** {humor:.1f}/10\n💤 **Sommeil moyen :** {sueno:.1f}h/nuit\n\n✨ *Bravo pour votre régularité ! N'oubliez pas que vous pouvez télécharger votre rapport médical en PDF avec /rapport.*",

    # Clinical PDF
    "pdf_generating": "📄 **Génération de votre rapport clinique PDF en cours...** Un instant s'il vous plaît...",
    "pdf_no_data": "🌸 **Avis :** Aucun enregistrement trouvé. Commencez avec `/registrar`.",
    "pdf_caption": "📄 **Voici votre rapport clinique au format PDF**, prêt à être présenté lors de votre consultation médicale ou à conserver dans vos archives.",
    "pdf_col_date": "Date",
    "pdf_col_energy": "Energie",
    "pdf_col_mood": "Humeur",
    "pdf_col_sleep": "Sommeil (h)",
    "pdf_col_medication": "Medicament",
    "pdf_col_notes": "Notes / Observations",
    "pdf_report_title": "RAPPORT CLINIQUE DE BIEN-ETRE ET DE STABILITE",
    "pdf_report_subtitle": "Suivi psycho-affectif de l'energie, de l'humeur et du sommeil",

    # Language Selection
    "lang_select_title": "🌐 **Sélection de la langue / Language Selection / Selección de Idioma**\n\nVeuillez choisir votre langue préférée :",
    "lang_changed": "✅ **Langue changée en Français avec succès.**",

    # Dashboard
    "dashboard_btn": "📊 Ouvrir Mon Tableau de Bord",
    "dashboard_msg": "✨ **Votre Tableau de Bord Privé de Bien-être**\n\nAppuyez sur le bouton ci-dessous pour afficher vos graphiques de stabilité, consulter votre assistant IA et télécharger votre rapport médical en PDF pour vos rendez-vous :",

    # Cancel & Reminder Off
    "cancel_msg": "❌ Suivi annulé. Vous pouvez recommencer à tout moment en utilisant /registrar.",
    "reminder_disabled": "🔕 Rappel quotidien désactivé.",

    # Help
    "help_text": "🤖 **Bot-Bip - Commandes de soutien et de suivi**\n\n• `/enregistrer` (`/registrar`) - Suivi quotidien (Énergie, Humeur, Sommeil & Médication).\n• `/rapport` (`/informe`) - Recevoir votre **Rapport Clinique PDF** directement dans le chat.\n• `/resume_hebdo` (`/resumen_semanal`) - Voir vos moyennes de stabilité sur 7 jours.\n• `/tableaudebord` (`/dashboard`) - Ouvrir votre tableau de bord interactif dans le navigateur.\n• `/calme` (`/calma`) - Espace de relaxation et boutons d'appel/message rapide vers votre **Réseau de soutien**.\n• `/contact` (`/contacto`) - Ajouter une personne de confiance.\n• `/rappel` (`/recordatorio`) - Configurer l'heure de votre notification quotidienne.\n• `/langue` (`/idioma`) - Changer de langue (Espagnol, Anglais, Français).\n• `/annuler` (`/cancelar`) - Annuler le suivi en cours.\n• `/aide` (`/ayuda`) - Afficher ce message d'aide."
}
