import os
import threading
import requests

from flask import Flask
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("BOT_TOKEN")

# =========================
# RENDER WEB SERVER
# =========================

web = Flask(__name__)


@web.route("/")
def home():
    return "🎵 Music Bot ishlayapti!"


def run_web():
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    await update.message.reply_text(
        "🎵 MUSIQA BOT\n\n"
        "🎤 Qo‘shiqchi yoki guruh nomini yozing.\n\n"
        "Masalan:\n"
        "Yulduz\n"
        "The Weeknd\n"
        "Drake\n"
        "Adele"
    )


# =========================
# QIDIRUV
# =========================

async def search_artist(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.strip()

    if not text:
        return

    # =========================
    # RAQAM YUBORILSA
    # =========================

    if text.isdigit():

        number = int(text)

        songs = context.user_data.get("songs", [])

        if not songs:
            await update.message.reply_text(
                "❗ Avval qo‘shiqchi nomini yozing."
            )
            return

        if number < 1 or number > len(songs):

            await update.message.reply_text(
                f"❌ Iltimos, 1 dan {len(songs)} gacha raqam yuboring."
            )

            return

        song = songs[number - 1]

        name = song["name"]
        artist = song["artist"]
        preview = song["preview"]

        if not preview:

            await update.message.reply_text(
                f"🎵 {name}\n\n"
                "⚠️ Bu qo‘shiq uchun 30 soniyalik preview mavjud emas."
            )

            return

        await update.message.reply_text(
            f"🎧 {name}\n"
            f"🎤 {artist}\n\n"
            "⏳ Audio tayyorlanmoqda..."
        )

        try:

            await update.message.reply_audio(
                audio=preview,
                title=name,
                performer=artist
            )

        except Exception as e:

            print("AUDIO XATO:", e)

            await update.message.reply_text(
                "❌ Audioni yuborishda xatolik yuz berdi."
            )

        return

    # =========================
    # QO‘SHIQCHI NOMI
    # =========================

    artist_name = text

    await update.message.reply_text(
        f"🔎 «{artist_name}» qidirilmoqda..."
    )

    try:

        response = requests.get(
            "https://itunes.apple.com/search",

            params={
                "term": artist_name,
                "entity": "song",
                "attribute": "artistTerm",
                "limit": 50
            },

            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        results = data.get("results", [])

        if not results:

            await update.message.reply_text(
                "❌ Qo‘shiqchi topilmadi."
            )

            return

        songs = []

        used = set()

        # =========================
        # 10 TA QO‘SHIQ
        # =========================

        for song in results:

            name = song.get("trackName")
            artist = song.get("artistName")
            preview = song.get("previewUrl")

            if not name:
                continue

            if name.lower() in used:
                continue

            used.add(name.lower())

            songs.append({
                "name": name,
                "artist": artist or artist_name,
                "preview": preview
            })

            if len(songs) == 10:
                break

        if not songs:

            await update.message.reply_text(
                "❌ Qo‘shiqlar topilmadi."
            )

            return

        # Saqlab qo‘yamiz
        context.user_data["songs"] = songs

        # =========================
        # TEXT RO‘YXAT
        # =========================

        message = (
            f"🎤 {artist_name}\n\n"
            "🔥 TOP 10 QO‘SHIQ:\n\n"
        )

        for i, song in enumerate(songs, 1):

            message += (
                f"{i}. {song['name']}\n"
            )

        message += (
            "\n━━━━━━━━━━━━━━\n"
            "🎧 Eshitish uchun qo‘shiq raqamini yuboring.\n\n"
            "Masalan: 3"
        )

        await update.message.reply_text(message)

    except requests.exceptions.RequestException as e:

        print("INTERNET XATO:", e)

        await update.message.reply_text(
            "⚠️ Internet yoki musiqa bazasida xatolik."
        )

    except Exception as e:

        print("XATO:", e)

        await update.message.reply_text(
            "❌ Xatolik yuz berdi."
        )


# =========================
# MAIN
# =========================

def main():

    if not TOKEN:

        print("❌ BOT_TOKEN topilmadi!")

        return

    # Render porti
    threading.Thread(
        target=run_web,
        daemon=True
    ).start()

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

    print("🎵 BOT ISHLADI!")

    app.run_polling()


if __name__ == "__main__":
    main()
