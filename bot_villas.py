import json
from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters, ConversationHandler
)

# Ton token de bot (NE LE PARTAGE PAS PUBLIQUEMENT)
BOT_TOKEN = "7782227100:AAFojxpSuFN6huEh0epqaMCXVk6A7TD2bR0"

# Ton ID Telegram (c’est ici que les réservations seront envoyées)
ADMIN_CHAT_ID = 7782227100

# Étapes de la conversation
COLLECTING_INFO = 1

# Charger les villas depuis un fichier JSON
def load_villas():
    with open("villas.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Quand l'utilisateur tape /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Voir les villas disponibles", callback_data="voir_villas")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🏡 Bienvenue dans notre service de réservation de villas !", reply_markup=reply_markup)

# Afficher la liste des villas
async def show_villas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    villas = load_villas()
    keyboard = [
        [InlineKeyboardButton(v["nom"], callback_data=f"villa_{v['id']}")] for v in villas
    ]
    await query.edit_message_text("Voici nos villas disponibles :", reply_markup=InlineKeyboardMarkup(keyboard))

# Afficher les détails d’une villa
async def show_villa_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    villa_id = query.data.replace("villa_", "")
    villas = load_villas()
    villa = next((v for v in villas if v["id"] == villa_id), None)

    if not villa:
        await query.edit_message_text("❌ Villa non trouvée.")
        return

    context.user_data["selected_villa"] = villa

    caption = f"🏠 *{villa['nom']}*\n💰 {villa['prix']}\n📝 {villa['description']}"
    buttons = [[InlineKeyboardButton("Réserver", callback_data="reserver")]]
    await query.message.delete()
    await context.bot.send_photo(
        chat_id=query.message.chat.id,
        photo=villa["photo_url"],
        caption=caption,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Demander les infos de réservation
async def ask_reservation_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "📝 Merci de me donner vos infos de réservation comme ceci :\n\n"
        "`Prénom, date, nombre de nuits`\n\n"
        "Exemple : *Yanis, 15 août, 2 nuits*",
        parse_mode="Markdown"
    )
    return COLLECTING_INFO

# Réception des infos utilisateur et envoi à l’admin
async def receive_reservation_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info = update.message.text
    villa = context.user_data.get("selected_villa")

    if not villa:
        await update.message.reply_text("❌ Une erreur est survenue. Réessayez depuis le début.")
        return ConversationHandler.END

    message = (
        f"📢 *Nouvelle réservation !*\n\n"
        f"*Villa :* {villa['nom']}\n"
        f"*Client :* {info}\n"
        f"*Prix :* {villa['prix']}"
    )

    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message, parse_mode="Markdown")
    await update.message.reply_text("✅ Merci ! Ta demande a bien été envoyée. On te recontacte vite 📩")
    return ConversationHandler.END

# Annuler la conversation
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚫 Réservation annulée.")
    return ConversationHandler.END

# Lancer le bot
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Conversation pour la réservation
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(ask_reservation_info, pattern="^reserver$")],
        states={
            COLLECTING_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_reservation_info)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Ajouter les handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_villas, pattern="^voir_villas$"))
    app.add_handler(CallbackQueryHandler(show_villa_details, pattern="^villa_"))
    app.add_handler(conv_handler)

    print("🤖 Le bot tourne... Appuie sur Ctrl+C pour arrêter.")
    app.run_polling()

if __name__ == "__main__":
    main()
