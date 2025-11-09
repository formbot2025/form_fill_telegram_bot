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

# --- AYARLAR ---
BOT_TOKEN = "8489494630:AAEtPQ323BhYSo0KTkaSjPZ41aUPlMs2kxk"
OWNER_CHAT_ID = 1811519811
TEMPLATE_PATH = "template.jpg"  # Görseli bu isimle aynı klasöre koy

FONTS = {
    "Arial": "arial.ttf",
    "Arial Black": "arialbd.ttf",
    "Times New Roman": "times.ttf",
    "Times New Roman Bold": "timesbd.ttf"
}
DEFAULT_SIZE = 18

STYLE_MAP = {
    "VERİLDİĞİ İL İLÇE": {"color": "#2b2b2b", "font": "Arial"},
    "PLAKA": {"color": "#000000", "font": "Arial Black"},
    "TESCİL SIRA NO": {"color": "#2b2b2b", "font": "Arial"},
    "MARKASI": {"color": "#2b2b2b", "font": "Arial"},
    "TİCARİ ADI": {"color": "#2b2b2b", "font": "Arial"},
    "CİNSİ": {"color": "#2b2b2b", "font": "Arial"},
    "CİNSİ2": {"color": "#2b2b2b", "font": "Arial"},
    "İLK TESCİL TARİHİ": {"color": "#2b2b2b", "font": "Arial"},
    "TESCİL TARİHİ": {"color": "#000000", "font": "Arial Black"},
    "TİPİ": {"color": "#2b2b2b", "font": "Arial"},
    "MODEL YILI": {"color": "#2b2b2b", "font": "Arial"},
    "ARAÇ SINIFI": {"color": "#2b2b2b", "font": "Arial"},
    "RENGİ": {"color": "#2b2b2b", "font": "Arial"},
    "MOTOR NO": {"color": "#000000", "font": "Arial Black"},
    "ŞASE NO": {"color": "#000000", "font": "Arial Black"},
    "NET AĞIRLIĞI": {"color": "#2b2b2b", "font": "Arial"},
    "KATAR AĞIRLIĞI": {"color": "#2b2b2b", "font": "Arial"},
    "KOLTUK SAYISI": {"color": "#2b2b2b", "font": "Arial"},
    "SİLİNDİR HACMİ": {"color": "#2b2b2b", "font": "Arial"},
    "YAKIT CİNSİ": {"color": "#2b2b2b", "font": "Arial"},
    "KULLANIM AMACI": {"color": "#2b2b2b", "font": "Arial"},
    "AZAMİ YÜKLÜ AĞIRLIĞI:": {"color": "#2b2b2b", "font": "Arial"},
    "RÖMORK AZAMİ YÜKLÜ AĞIRLIĞI": {"color": "#2b2b2b", "font": "Arial"},
    "MOTOR GÜCÜ": {"color": "#2b2b2b", "font": "Arial"},
    "TİP ONAY": {"color": "#2b2b2b", "font": "Arial"},
    "TC KİMLİK": {"color": "#000000", "font": "Arial Black"},
    "SOYADI": {"color": "#2b2b2b", "font": "Arial"},
    "ADI": {"color": "#2b2b2b", "font": "Arial"},
    "ADRESİ": {"color": "#2b2b2b", "font": "Arial"},
    "ADRES 2": {"color": "#2b2b2b", "font": "Arial"},
    "MUAYENE GEÇERLİK": {"color": "#2b2b2b", "font": "Arial"},
    "SİC NO.": {"color": "#19417A", "font": "Times New Roman", "size": 21},
    "SERİ NO": {"color": "#000000", "font": "Times New Roman Bold", "size": 26},
    "NO": {"color": "#000000", "font": "Times New Roman Bold", "size": 26}
}

coords = {
    "VERİLDİĞİ İL İLÇE": {"x": 56, "y": 84},
    "PLAKA": {"x": 53, "y": 141},
    "TESCİL SIRA NO": {"x": 94, "y": 195},
    "MARKASI": {"x": 57, "y": 254},
    "TİCARİ ADI": {"x": 57, "y": 305},
    "CİNSİ": {"x": 147, "y": 336},
    "CİNSİ2": {"x": 55, "y": 360},
    "İLK TESCİL TARİHİ": {"x": 322, "y": 140},
    "TESCİL TARİHİ": {"x": 322, "y": 196},
    "TİPİ": {"x": 430, "y": 251},
    "MODEL YILI": {"x": 365, "y": 307},
    "ARAÇ SINIFI": {"x": 515, "y": 307},
    "RENGİ": {"x": 419, "y": 362},
    "MOTOR NO": {"x": 257, "y": 417},
    "ŞASE NO": {"x": 211, "y": 472},
    "NET AĞIRLIĞI": {"x": 60, "y": 527},
    "KATAR AĞIRLIĞI": {"x": 60, "y": 582},
    "KOLTUK SAYISI": {"x": 60, "y": 638},
    "SİLİNDİR HACMİ": {"x": 60, "y": 696},
    "YAKIT CİNSİ": {"x": 60, "y": 753},
    "KULLANIM AMACI": {"x": 60, "y": 809},
    "AZAMİ YÜKLÜ AĞIRLIĞI:": {"x": 529, "y": 519},
    "RÖMORK AZAMİ YÜKLÜ AĞIRLIĞI": {"x": 487, "y": 574},
    "MOTOR GÜCÜ": {"x": 545, "y": 680},
    "TİP ONAY": {"x": 322, "y": 809},
    "TC KİMLİK": {"x": 868, "y": 85},
    "SOYADI": {"x": 833, "y": 137},
    "ADI": {"x": 784, "y": 194},
    "ADRESİ": {"x": 653, "y": 261},
    "ADRES 2": {"x": 652, "y": 282},
    "MUAYENE GEÇERLİK": {"x": 657, "y": 595},
    "SİC NO.": {"x": 697, "y": 808},
    "SERİ NO": {"x": 968, "y": 798},
    "NO": {"x": 1055, "y": 798}
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
    await update.message.reply_text("Merhaba! Şimdi bilgileri sırasıyla gireceksiniz.\nİlk alan: " + fields[0])
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
