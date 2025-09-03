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
ADMIN_CHAT_ID = 6933858510  # جایگزین کن
FONT_PATH = "Vazirmatn-Regular.ttf"

app = Flask(__name__, static_folder="static", template_folder="templates")
bot = telebot.TeleBot(TOKEN)

# ---------------- Products ----------------
products = {
    "3390": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 697000, "category": "women", "image": "https://raw.githubusercontent.com/artintaleei90/Site/main/IMG_0394.jpeg"},
    "1107": {"name": "فری سایز - پک 6 عددی رنگ: سفید و مشکی", "price": 547000, "category": "women", "image": "https://raw.githubusercontent.com/artintaleei90/Site/main/IMG_0395.jpeg"},
}

# ---------------- Register Font ----------------
if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont('Vazir', FONT_PATH))
else:
    print("⚠️ فونت فارسی Vazirmatn-Regular.ttf پیدا نشد!")

def reshape_text(text: str) -> str:
    try:
        return get_display(arabic_reshaper.reshape(str(text)))
    except Exception:
        return str(text)

# ---------------- PDF creation ----------------
def create_pdf(filename: str, data: dict):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    c.setFont("Vazir" if os.path.exists(FONT_PATH) else "Helvetica", 16)
    c.drawCentredString(width/2, height - 2*cm, reshape_text("🧾 فاکتور سفارش"))

    c.setFont("Vazir" if os.path.exists(FONT_PATH) else "Helvetica", 12)
    y = height - 3.2 * cm
    customer_lines = [
        f"نام مشتری: {data.get('name','')}",
        f"شماره تماس: {data.get('phone','')}",
        f"شهر: {data.get('city','')}",
        f"آدرس: {data.get('address','')}",
    ]
    for line in customer_lines:
        c.drawRightString(width - 2*cm, y, reshape_text(line))
        y -= 0.8*cm

    y -= 0.2*cm
    orders = data.get('orders', [])
    if not orders:
        c.drawRightString(width - 2*cm, y, reshape_text("هیچ محصولی ثبت نشده است."))
        c.showPage()
        c.save()
        return

    table_data = [
        [reshape_text("کد محصول"), reshape_text("نام محصول"), reshape_text("تعداد"), reshape_text("قیمت واحد"), reshape_text("مبلغ کل")]
    ]
    total = 0
    for o in orders:
        code = o.get('code','')
        name = o.get('name','')
        count = int(o.get('count',0))
        price = int(o.get('price',0))
        sum_price = count * price
        total += sum_price
        table_data.append([
            reshape_text(code),
            reshape_text(name),
            reshape_text(str(count)),
            reshape_text(f"{price:,}"),
            reshape_text(f"{sum_price:,}")
        ])

    table = Table(table_data, colWidths=[3*cm, 7*cm, 2*cm, 3*cm, 3*cm])
    style = TableStyle([
        ('GRID', (0,0), (-1,-1), 0.6, colors.HexColor("#cccccc")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f2f2f2")),
        ('FONTNAME', (0,0), (-1,-1), 'Vazir' if os.path.exists(FONT_PATH) else 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ])
    table.setStyle(style)
    table.wrapOn(c, width, height)
    table.drawOn(c, 2*cm, y - (len(table_data) * 1.1 * cm))

    y = y - (len(table_data) * 1.1 * cm) - 0.8*cm
    c.setFont("Vazir" if os.path.exists(FONT_PATH) else "Helvetica", 12)
    c.drawRightString(width - 2*cm, y, reshape_text(f"جمع کل: {total:,} تومان"))

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

    # ارسال PDF به تلگرام
    try:
        with open(filename, "rb") as f:
            bot.send_document(ADMIN_CHAT_ID, f)
    except Exception as e:
        print("❌ خطا در ارسال به تلگرام:", e)

    # بازگشت PDF به کاربر
    response = send_file(filename, mimetype='application/pdf', as_attachment=True)
    try:
        os.remove(filename)
    except:
        pass
    return response

# ---------------- Run Flask ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
