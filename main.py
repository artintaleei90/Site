import os
from flask import Flask, request, jsonify, send_file, render_template
import telebot

from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

import arabic_reshaper
from bidi.algorithm import get_display

# ---------------- CONFIG ----------------
TOKEN = "7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE"
ADMIN_CHAT_ID = 6933858510  # جایگذاری با chat id خودت
WEBHOOK_URL = "https://halstonshop.onrender.com/webhook"

FONT_PATH = "Vazirmatn-Regular.ttf"

app = Flask(__name__, static_folder="static", template_folder="templates")
bot = telebot.TeleBot(TOKEN)

# ---------------- Products ----------------
products = {
    "3390": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 697000, "category": "women", "image": "https://raw.githubusercontent.com/artintaleei90/Site/main/IMG_0394.jpeg"},
    "1107": {"name": "فری سایز - پک 6 عددی رنگ: سفید و مشکی", "price": 547000, "category": "women", "image": "https://raw.githubusercontent.com/artintaleei90/Site/main/IMG_0395.jpeg"},
    # محصولات بیشتر اینجا اضافه کن
}

# ---------------- Register Font ----------------
if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont('Vazir', FONT_PATH))
else:
    print("هشدار: فونت فارسی Vazirmatn-Regular.ttf پیدا نشد.")

def reshape_text(text: str) -> str:
    try:
        return get_display(arabic_reshaper.reshape(str(text)))
    except Exception:
        return str(text)

# ---------------- PDF creation ----------------
def create_pdf(filename, data):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # عنوان فاکتور
    c.setFont("Vazir", 16)
    c.drawCentredString(width / 2, height - 2*cm, reshape_text("🧾 فاکتور سفارش"))

    # اطلاعات مشتری
    c.setFont("Vazir", 12)
    y = height - 4*cm
    customer_info = [
        f"نام مشتری: {data.get('name','')}",
        f"شماره تماس: {data.get('phone','')}",
        f"شهر: {data.get('city','')}",
        f"آدرس: {data.get('address','')}"
    ]
    for line in customer_info:
        c.drawRightString(width - 2*cm, y, reshape_text(line))
        y -= 1*cm

    y -= 0.5*cm

    # جدول سفارشات
    orders = data.get('orders', [])
    if not orders:
        c.drawString(2*cm, y, reshape_text("هیچ محصولی ثبت نشده است."))
        c.showPage()
        c.save()
        return

    table_data = [[
        reshape_text("کد محصول"),
        reshape_text("نام محصول"),
        reshape_text("تعداد"),
        reshape_text("قیمت واحد"),
        reshape_text("مبلغ کل")
    ]]

    total_price = 0
    for order in orders:
        code = order.get('code','')
        name = order.get('name','')
        count = int(order.get('count',0))
        price = int(order.get('price',0))
        sum_price = count * price
        total_price += sum_price
        table_data.append([
            reshape_text(code),
            reshape_text(name),
            reshape_text(str(count)),
            reshape_text(f"{price:,}"),
            reshape_text(f"{sum_price:,}")
        ])

    table = Table(table_data, colWidths=[3*cm, 7*cm, 2*cm, 3*cm, 3*cm])
    style = TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('FONTNAME', (0,0), (-1,-1), 'Vazir'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ])
    table.setStyle(style)
    table.wrapOn(c, width, height)
    table_height = table._height
    table.drawOn(c, 2*cm, y - table_height)

    y = y - table_height - 1*cm
    c.setFont("Vazir", 12)
    c.drawRightString(width - 2*cm, y, reshape_text(f"جمع کل سفارش: {total_price:,} تومان"))

    # اطلاعات بانک
    y -= 1.5*cm
    bank_text = [
        "💳بانک سامان - آزیتا فتوحی مظفرنژاد",
        "6219-8610-6509-3089",
        "IR440560083280078294010001",
        "",
        "👈🏼 واریز وجه تنها به شماره کارت های دریافتی از شماره تماس 09128883343 دارای اعتبار می باشد.",
        "",
        "📣 همکار گرامی تنها پس از تایید وجه در بانک مقصد، امکان خروجی از انبار میسر است.",
        "",
        "🛑لذا خواهشمندیم نسبت به انتقال وجه به صورت کارت به کارت، شبا، پایا ... توجه فرمایید."
    ]
    for line in bank_text:
        c.drawRightString(width - 2*cm, y, reshape_text(line))
        y -= 0.7*cm

    c.showPage()
    c.save()

# ---------------- Flask routes ----------------
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/api/products', methods=['GET'])
def api_products():
    return jsonify(products)

@app.route('/api/order', methods=['POST'])
def api_order():
    data = request.json or {}
    name = data.get("name","")
    phone = data.get("phone","")
    city = data.get("city","")
    address = data.get("address","")
    cart_items = data.get("cart", [])

    orders = []
    for it in cart_items:
        code = str(it.get("code",""))
        count = int(it.get("count",0))
        prod = products.get(code)
        if not prod:
            continue
        orders.append({
            "code": code,
            "name": prod["name"],
            "price": prod["price"],
            "count": count
        })

    pdf_data = {
        "name": name,
        "phone": phone,
        "city": city,
        "address": address,
        "orders": orders
    }

    filename = f"invoice_{phone or 'guest'}.pdf"
    create_pdf(filename, pdf_data)

    # Send PDF to admin
    try:
        with open(filename, "rb") as f:
            bot.send_document(ADMIN_CHAT_ID, f)
    except Exception as e:
        print("خطا در ارسال به تلگرام:", e)

    # Return PDF to user
    response = send_file(filename, mimetype='application/pdf', as_attachment=False)
    try:
        os.remove(filename)
    except Exception:
        pass
    return response

# ---------------- Webhook for Telegram ----------------
@app.route('/webhook', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# ---------------- Run Flask ----------------
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=8080)
