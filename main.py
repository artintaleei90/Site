from flask import Flask, render_template, request, send_file, jsonify
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
import arabic_reshaper
from bidi.algorithm import get_display
import requests
import os
from collections import defaultdict

app = Flask(__name__)

# ---------------------- محصولات ----------------------
products = {
    "3390": {
        "name": "فری سایز - پک 6 عددی رنگ: در تصویر",
        "price": 697000,
        "unit": "هزار تومان",
        "category": "زنانه",
        "image": "https://raw.githubusercontent.com/artintaleei90/Site/main/IMG_0394.jpeg"
    },
    "1107": {
        "name": "فری سایز - پک 6 عددی رنگ: سفید و مشکی",
        "price": 547000,
        "unit": "هزار تومان",
        "category": "زنانه",
        "image": "https://raw.githubusercontent.com/artintaleei90/Site/main/IMG_0395.jpeg"
    },
}

# گروه‌بندی محصولات بر اساس دسته‌بندی
def group_products_by_category():
    grouped = defaultdict(list)
    for code, data in products.items():
        grouped[data["category"]].append({**data, "code": code})
    return dict(grouped)

# اطلاعات مدیر برای ارسال PDF
ADMIN_CHAT_ID = 6933858510
TELEGRAM_TOKEN = "7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE"

# ثبت فونت فارسی
FONT_PATH = "Vazirmatn-Regular.ttf"
if not os.path.exists(FONT_PATH):
    raise Exception("فونت فارسی پیدا نشد! لطفا Vazirmatn-Regular.ttf را کنار فایل قرار بده.")
pdfmetrics.registerFont(TTFont('Vazir', FONT_PATH))

def reshape_text(text):
    return get_display(arabic_reshaper.reshape(text))

# ---------------------- صفحه اصلی ----------------------
@app.route('/')
def index():
    grouped_products = group_products_by_category()
    return render_template("index.html", products=grouped_products)

# ---------------------- API محصولات ----------------------
@app.route('/api/products')
def api_products():
    return jsonify(products)

# ---------------------- ثبت سفارش ----------------------
@app.route('/checkout', methods=['POST'])
def checkout():
    data = request.json
    cart = data.get("cart", [])

    # ساخت فاکتور PDF
    filename = "invoice.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    y_start = height - 2 * cm

    # عنوان فاکتور
    c.setFont("Vazir", 16)
    c.drawCentredString(width / 2, y_start, reshape_text("🧾 فاکتور سفارش"))
    y = y_start - 2 * cm

    # جدول محصولات
    table_data = [
        [reshape_text("کد محصول"), reshape_text("نام محصول"), reshape_text("قیمت")]
    ]
    total = 0
    for item in cart:
        code = item["code"]
        product = products.get(code)
        if product:
            price = product["price"]
            total += price
            table_data.append([
                reshape_text(code),
                reshape_text(product["name"]),
                reshape_text(str(price))
            ])

    table = Table(table_data, colWidths=[3 * cm, 8 * cm, 4 * cm])
    style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, -1), 'Vazir'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ])
    table.setStyle(style)
    table.wrapOn(c, width, height)
    table.drawOn(c, 2 * cm, y - len(table_data) * 1.2 * cm)
    y -= (len(table_data) * 1.2 * cm + 1 * cm)

    # جمع کل
    c.drawRightString(width - 2 * cm, y, reshape_text(f"جمع کل: {total:,} تومان"))
    y -= 1 * cm

    c.save()

    # ارسال PDF به مدیر
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    with open(filename, "rb") as f:
        requests.post(url, data={"chat_id": ADMIN_CHAT_ID}, files={"document": f})

    return jsonify({"status": "ok", "message": "فاکتور ارسال شد!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
