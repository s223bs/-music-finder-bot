import os
import threading
import requests

from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("BOT_TOKEN")

# Render uchun web server
web = Flask(__name__)

@web.route("/")
def home():
    return "🎵 Music Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 MUSIQA BOT\n\n"
        "🎤 Qo‘shiqchi yoki guruh nomini yozing.\n\n"
        "Masalan:\n"
        "The Weeknd\n"
        "Drake\n"
        "Adele"
    )


async def search_artist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    artist = update.message.text.strip()

    if not artist:
        return

    await update.message.reply_text(
        f"🔎 «{artist}» musiqalari qidirilmoqda..."
    )

    try:
        response = requests.get(
            "https://itunes.apple.com/search",
            params={
                "term": artist,
                "entity": "song",
                "limit": 50
            },
            timeout=15
        )

        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])

        if not results:
            await update.message.reply_text(
                "❌ Bu qo‘shiqchi topilmadi."
            )
            return

        buttons = []

        for song in results[:20]:
            name = song.get("trackName")
            link = song.get("trackViewUrl")

            if name and link:
                buttons.append([
                    InlineKeyboardButton(
                        f"🎵 {name}",
                        url=link
                    )
                ])

        if not buttons:
            await update.message.reply_text(
                "❌ Qo‘shiqlar topilmadi."
            )
            return

        await update.message.reply_text(
            f"🎤 {artist}\n\n"
            f"🎶 {len(results)} ta qo‘shiq topildi.\n\n"
            "Qo‘shiqni tanlang 👇",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    except Exception as e:
        print("XATO:", e)
        await update.message.reply_text(
            "⚠️ Xatolik yuz berdi."
        )


def main():
    if not TOKEN:
        print("❌ BOT_TOKEN topilmadi!")
        return

    # Web serverni alohida ishga tushiramiz
    threading.Thread(
        target=run_web,
        daemon=True
    ).start()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            search_artist
        )
    )

    print("🎵 Bot ishga tushdi!")

    app.run_polling()


if __name__ == "__main__":
    main()
