from flask import Flask, render_template, request, send_file, send_from_directory
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

app = Flask(__name__)

# ---------------------- محصولات ----------------------
products = {
    "3390": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 697000, "unit": "هزار تومان","category":"women","image":"https://raw.githubusercontent.com/artintaleei90/Site/main/IMG_0394.jpeg"},
    "1107": {"name": "فری سایز - پک 6 عددی رنگ: سفید و مشکی", "price": 547000, "unit": "هزار تومان","category":"women","image":"https://raw.githubusercontent.com/artintaleei90/Site/main/IMG_0395.jpeg"},
}

# اطلاعات مدیر برای ارسال PDF
ADMIN_CHAT_ID = 6933858510
TELEGRAM_TOKEN ="7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE"

# ثبت فونت فارسی
FONT_PATH = "Vazirmatn-Regular.ttf"
if not os.path.exists(FONT_PATH):
    raise Exception("فونت فارسی پیدا نشد! لطفا Vazirmatn-Regular.ttf را کنار فایل قرار بده.")
pdfmetrics.registerFont(TTFont('Vazir', FONT_PATH))

def reshape_text(text):
    return get_display(arabic_reshaper.reshape(text))

# ---------------------- روت اصلی ----------------------
@app.route('/')
def index():
    return render_template("index.html", products=products)

# ---------------------- دسته‌بندی محصولات ----------------------
@app.route('/contact')
def contact():
    return "<h1>تماس با ما</h1><p>شماره تماس: 0912xxxxxxx</p>"

@app.route('/category/<category_name>')
def category(category_name):
    filtered_products = {k:v for k,v in products.items() if v.get("category") == category_name}
    return render_template("index.html", products=filtered_products)

# ---------------------- ثبت سفارش ----------------------
@app.route('/order', methods=['POST'])
def order():
    name = request.form.get("name")
    phone = request.form.get("phone")
    address = request.form.get("address")
    order_codes = request.form.getlist("order_code")
    order_counts = request.form.getlist("order_count")

    filename = f"invoice_{phone}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    y_start = height - 2*cm

    # عنوان فاکتور
    c.setFont("Vazir", 16)
    c.drawCentredString(width/2, y_start, reshape_text("🧾 فاکتور سفارش"))
    y = y_start - 2*cm

    # اطلاعات مشتری
    c.setFont("Vazir", 12)
    c.drawRightString(width - 2*cm, y, reshape_text(f"نام مشتری: {name}"))
    y -= 1*cm
    c.drawRightString(width - 2*cm, y, reshape_text(f"شماره تماس: {phone}"))
    y -= 1*cm
    c.drawRightString(width - 2*cm, y, reshape_text(f"آدرس: {address}"))
    y -= 1.5*cm

    # جدول محصولات
    table_data = [
        [reshape_text("کد محصول"), reshape_text("نام محصول"), reshape_text("تعداد"), reshape_text("قیمت واحد"), reshape_text("مبلغ کل")]
    ]
    total = 0
    for code, count in zip(order_codes, order_counts):
        count = int(count)
        product = products.get(code)
        if product:
            price = product["price"]
            sum_price = price * count
            total += sum_price
            table_data.append([
                reshape_text(code),
                reshape_text(product["name"]),
                reshape_text(str(count)),
                reshape_text(str(price)),
                reshape_text(str(sum_price))
            ])

    table = Table(table_data, colWidths=[3*cm, 7*cm, 2*cm, 3*cm, 3*cm])
    style = TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('FONTNAME', (0,0), (-1,-1), 'Vazir'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
    ])
    table.setStyle(style)
    table.wrapOn(c, width, height)
    table.drawOn(c, 2*cm, y - len(table_data)*1.2*cm)
    y -= (len(table_data)*1.2*cm + 1*cm)

    # جمع کل
    c.drawRightString(width - 2*cm, y, reshape_text(f"جمع کل: {total} تومان"))
    y -= 1*cm

    # اطلاعات پرداخت
    bank_info_lines = [    
        "شماره :۰۹۱۲۸۸۸۳۳۴۳(واتساپ)",
        "فاکتور رو برای شماره بالا ارسال و نهایی کنید",
        "بانک سامان",
        "به نام: آزیتا فتوحی مظفرنژاد",
        "شماره کارت: 6219-8610-6509-3089",
        "شماره شبا: IR44 0560 0832 8007 8294 0100 01"
    ]
    c.setFont("Vazir", 10)
    for line in bank_info_lines:
        c.drawRightString(width - 2*cm, y, reshape_text(line))
        y -= 0.8*cm

    c.save()

    # ارسال PDF به مدیر
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    with open(filename, "rb") as f:
        requests.post(url, data={"chat_id": ADMIN_CHAT_ID}, files={"document": f})

    # نمایش PDF به کاربر
    return send_file(filename, as_attachment=True)

# ---------------------- روت گوگل ورریفیکیشن ----------------------
@app.route('templates/googlef45b12f9e985ca0c.html')
def google_verify():
    return send_from_directory(os.getcwd(), 'googlef45b12f9e985ca0c.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
