#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ruhsat_doldurucu_final.py
# Render-ready — kullanıcının girdiği alanları template.jpg üzerine yazar ve yalnızca admin'e gönderir.

import os
import logging
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# --- AYARLAR (örnek token / örnek owner id — istersen kendiyle değiştir) ---
BOT_TOKEN = "8489494630:AAEtPQ323BhYSo0KTkaSjPZ41aUPlMs2kxk"
OWNER_CHAT_ID = 1811519811
TEMPLATE_PATH = "template.jpg"  # template dosyan template.jpg olmalı

# --- FONTLAR ---
FONTS = {
    "Arial": "arial.ttf",
    "Arial Black": "arialbd.ttf",
    "Times New Roman": "times.ttf",
    "Times New Roman Bold": "timesbd.ttf",
}
DEFAULT_SIZE = 14  # tüm alanlar için varsayılan boyut

# --- STYLE_MAP & KOORDİNATLAR ---
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
    "NO": {"color": "#000000", "font": "Times New Roman Bold", "size": 26},
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
    "NO": {"x": 1055, "y": 798},
}

# --- DİNAMİK DURUMLAR ---
WAITING_DATA = 0
SESSIONS = {}

# --- LOG ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- YARDIMCI FONKSİYONLAR ---
def load_font(font_key, size):
    """
    Font anahtarını (örn. "Arial") alır, FONTS haritasından .ttf yoluna bakar.
    Bulamazsa hata basar ve ImageFont.load_default() döner.
    """
    fontname = FONTS.get(font_key)
    if not fontname:
        logger.warning(f"Font anahtarı tanımlı değil: {font_key}. Varsayılan font kullanılacak.")
        return ImageFont.load_default()
    # yol göreli ise bu dosyanın bulunduğu klasöre göre çöz
    path = os.path.join(os.path.dirname(__file__), fontname) if "__file__" in globals() else fontname
    if not os.path.exists(path):
        logger.warning(f"Font dosyası bulunamadı: {path}. Varsayılan font kullanılacak.")
        return ImageFont.load_default()
    try:
        return ImageFont.truetype(path, size)
    except Exception as e:
        logger.exception(f"Font yüklenemedi ({path}): {e}")
        return ImageFont.load_default()

def render_image(data_map):
    """
    data_map: {field_name: text, ...}
    Template'i açar, her alanı coords ve STYLE_MAP kullanarak yazar,
    BytesIO olarak geri döner (JPEG).
    """
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Template bulunamadı: {TEMPLATE_PATH}")
    img = Image.open(TEMPLATE_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)

    for field, text in data_map.items():
        if not text:
            continue
        pos = coords.get(field)
        if not pos:
            continue
        style = STYLE_MAP.get(field, {"color": "#000000", "font": "Arial"})
        size = style.get("size", DEFAULT_SIZE)
        font_key = style.get("font", "Arial")
        font = load_font(font_key, size)
        # x,y pozisyonu
        x, y = pos["x"], pos["y"]
        draw.text((x, y), str(text), fill=style.get("color", "#000000"), font=font)

    bio = BytesIO()
    img.save(bio, "JPEG", quality=95)
    bio.seek(0)
    return bio

# --- HANDLER'lar ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    fields = list(coords.keys())
    SESSIONS[chat_id] = {"index": 0, "fields": {f: "" for f in fields}, "order": fields}
    await update.message.reply_text(
        "Merhaba! Şimdi bilgileri sırasıyla gireceksiniz.\nİptal için /cancel\nİlk alan: " + fields[0]
    )
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
    current_field = order[idx]
    session["fields"][current_field] = text
    idx += 1
    session["index"] = idx

    if idx < len(order):
        await update.message.reply_text(f"Sonraki alan: {order[idx]}")
        return WAITING_DATA
    else:
        await update.message.reply_text("Tüm alanlar alındı, görsel admin'e gönderiliyor...")
        out = render_image(session["fields"])
        # fotoğrafı sadece OWNER_CHAT_ID'ye gönder
        if OWNER_CHAT_ID:
            out.seek(0)
            try:
                await context.bot.send_photo(chat_id=OWNER_CHAT_ID, photo=out, caption=f"Yeni form — kullanıcı: {chat_id}")
                logger.info(f"Form görseli gönderildi -> OWNER: {OWNER_CHAT_ID}")
            except Exception as e:
                logger.exception(f"Admin'e fotoğraf gönderilemedi: {e}")
                await update.message.reply_text("Görsel oluşturuldu ama admin'e gönderilemedi (loglarda hata).")
        # kullanıcıya sadece bilgi ver
        await update.message.reply_text("Tamamlandı ✅ Yeni işlem için /start yazabilirsiniz.")
        SESSIONS.pop(chat_id, None)
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    SESSIONS.pop(chat_id, None)
    await update.message.reply_text("İşlem iptal edildi.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={WAITING_DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    logger.info("Bot başlatılıyor...")
    app.run_polling()

if __name__ == "__main__":
    main()
