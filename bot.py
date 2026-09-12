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

    url = "https://itunes.apple.com/search"

    params = {
        "term": artist,
        "entity": "song",
        "limit": 50
    }

    try:
        response = requests.get(
            url,
            params=params,
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

        # Faqat kerakli ma'lumotlarni saqlaymiz
        songs = []

        for song in results:
            name = song.get("trackName")
            artist_name = song.get("artistName")
            album = song.get("collectionName")
            link = song.get("trackViewUrl")
            preview = song.get("previewUrl")

            if name and link:
                songs.append({
                    "name": name,
                    "artist": artist_name,
                    "album": album,
                    "link": link,
                    "preview": preview
                })

        if not songs:
            await update.message.reply_text(
                "❌ Qo‘shiqlar topilmadi."
            )
            return

        # Telegram xabari juda uzun bo'lib ketmasligi uchun
        # birinchi 20 ta qo'shiqni chiqaramiz.
        buttons = []

        for song in songs[:20]:

            buttons.append([
                InlineKeyboardButton(
                    f"🎵 {song['name']}",
                    url=song["link"]
                )
            ])

        await update.message.reply_text(
            f"🎤 {artist}\n\n"
            f"🎶 {len(songs)} ta qo‘shiq topildi.\n\n"
            "Qo‘shiqni tanlang 👇",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    except requests.exceptions.RequestException:
        await update.message.reply_text(
            "⚠️ Internet yoki musiqa bazasida xatolik."
        )

    except Exception as e:
        print("XATO:", e)

        await update.message.reply_text(
            "⚠️ Xatolik yuz berdi. Keyinroq urinib ko‘ring."
        )


def main():

    if not TOKEN:
        print("❌ BOT_TOKEN topilmadi!")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

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
