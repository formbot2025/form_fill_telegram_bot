#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# form_fill_telegram_bot_v2_fixed.py
# Kullanıcıdan sadece metin ister, sabit görsel üzerine yazar.

import logging
import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, ConversationHandler, filters

BOT_TOKEN = "8489494630:AAEtPQ323BhYSo0KTkaSjPZ41aUPlMs2kxk"  # Telegram token
OWNER_CHAT_ID = 1811519811
TEMPLATE_PATH = "template.jpg"

FONTS = {
    "Arial": "arial.ttf",
    "Arial Black": "arialbd.ttf",
    "Times New Roman": "times.ttf",
    "Times New Roman Bold": "timesbd.ttf"
}
DEFAULT_SIZE = 18

STYLE_MAP = {
    "PLAKA": {"color": "#000000", "font": "Arial Black"}
}

coords = {
    "PLAKA": {"x": 53, "y": 141}
}

WAITING_DATA = 0
SESSIONS = {}

def load_font(font_key, size):
    path = FONTS.get(font_key)
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

def render_image(data_map):
    img = Image.open(TEMPLATE_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)
    for field, text in data_map.items():
        if not text:
            continue
        pos = coords.get(field)
        style = STYLE_MAP.get(field, {"color": "#000", "font": "Arial"})
        size = style.get("size", DEFAULT_SIZE)
        font = load_font(style["font"], size)
        draw.text((pos["x"], pos["y"]), text, fill=style["color"], font=font)
    bio = BytesIO()
    img.save(bio, "JPEG")
    bio.seek(0)
    return bio

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    fields = list(coords.keys())
    SESSIONS[chat_id] = {"index": 0, "fields": {f: "" for f in fields}, "order": fields}
    await update.message.reply_text("Merhaba! İlk alan: " + fields[0])
    return WAITING_DATA

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text.strip()
    session = SESSIONS.get(chat_id)
    if not session:
        await update.message.reply_text("Lütfen /start komutunu kullanın.")
        return ConversationHandler.END

    idx = session["index"]
    order = session["order"]
    session["fields"][order[idx]] = text
    idx += 1
    session["index"] = idx

    if idx < len(order):
        await update.message.reply_text(f"Sonraki alan: {order[idx]}")
        return WAITING_DATA
    else:
        await update.message.reply_text("Tüm alanlar alındı, görsel hazırlanıyor...")
        out = render_image(session["fields"])
        await context.bot.send_photo(chat_id=chat_id, photo=out)
        if OWNER_CHAT_ID:
            out.seek(0)
            await context.bot.send_photo(chat_id=OWNER_CHAT_ID, photo=out, caption=f"Yeni form {chat_id}")
        SESSIONS.pop(chat_id, None)
        await update.message.reply_text("Tamamlandı. Yeni işlem için /start yazabilirsiniz.")
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    SESSIONS.pop(chat_id, None)
    await update.message.reply_text("İşlem iptal edildi.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={WAITING_DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler)]},
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    app.add_handler(conv)
    print("Bot çalışıyor...")
    app.run_polling()

if __name__ == "__main__":
    main()
