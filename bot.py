import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 Salom!\n\n"
        "Qo‘shiqchi nomini yozing.\n"
        "Masalan: The Weeknd"
    )

async def search_artist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    artist = update.message.text.strip()

    await update.message.reply_text("🔎 Qidiryapman...")

    url = "https://itunes.apple.com/search"
    params = {
        "term": artist,
        "entity": "song",
        "limit": 10
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        results = data.get("results", [])

        if not results:
            await update.message.reply_text(
                "❌ Bu qo‘shiqchini topa olmadim."
            )
            return

        buttons = []

        for song in results:
            name = song.get("trackName", "Noma'lum")
            artist_name = song.get("artistName", "Noma'lum")
            link = song.get("trackViewUrl")

            if link:
                buttons.append([
                    InlineKeyboardButton(
                        f"🎵 {name} — {artist_name}",
                        url=link
                    )
                ])

        await update.message.reply_text(
            f"🎤 {artist} uchun top qo‘shiqlar:\n\n"
            "Quyidagilardan birini tanlang 👇",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    except Exception:
        await update.message.reply_text(
            "⚠️ Xatolik yuz berdi. Keyinroq urinib ko‘ring."
        )

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, search_artist)
    )

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
