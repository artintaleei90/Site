from flask import Flask, render_template, request, send_file
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

# محصولات نمونه
products = {
       "3390": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 697000, "unit": "هزار تومان"},
    "1107": {"name": "فری سایز - پک 6 عددی رنگ: سفید و مشکی", "price": 547000, "unit": "هزار تومان"},
    "1303": {"name": "فری سایز - پک 4 عددی رنگ: در تصویر به جز سبز", "price": 747000, "unit": "هزار تومان"},
    "3389": {"name": "فری سایز - پک 4 عددی رنگ: در تصویر (مانتو کتی)", "price": 797000, "unit": "هزار تومان"},
    "1106": {"name": "فری سایز - دو طرح رنگ: در تصویر", "price": 397000, "unit": "هزار تومان"},
    "1203": {"name": "فری سایز - پک 6 عددی رنگ: سفید", "price": 547000, "unit": "هزار تومان"},
    "1213": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 497000, "unit": "هزار تومان"},
    "3392": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر (کرم و مشکی)", "price": 597000, "unit": "هزار تومان"},
    "3357": {"name": "فری سایز - پک 5 عددی رنگ: در تصویر", "price": 427000, "unit": "هزار تومان"},
    "1108": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 647000, "unit": "هزار تومان"},
    "3346": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 597000, "unit": "هزار تومان"},
    "1204": {"name": "فری سایز - پک 5 عددی رنگ: در تصویر", "price": 597000, "unit": "هزار تومان"},
    "3340": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 567000, "unit": "هزار تومان"},
    "1114": {"name": "فری سایز - پک 7 عددی رنگ: در تصویر (PERRY ترک)", "price": 637000, "unit": "هزار تومان"},
    "1102": {"name": "فری سایز - پک 5 عددی رنگ: در تصویر", "price": 397000, "unit": "هزار تومان"},
    "1301": {"name": "فری سایز - پک 4 عددی رنگ: در تصویر", "price": 597000, "unit": "هزار تومان"},
    "3377": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 597000, "unit": "هزار تومان"},
    "3759": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 347000, "unit": "هزار تومان"},
    "1117": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 697000, "unit": "هزار تومان"},
    "3395": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 757000, "unit": "هزار تومان"},
    "3364": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 457000, "unit": "هزار تومان"},
    "1201": {"name": "فری سایز - پک 4 عددی رنگ: کرم", "price": 797000, "unit": "هزار تومان"},
    "3383": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 657000, "unit": "هزار تومان"},
    "1202": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 737000, "unit": "هزار تومان"},
    "1211": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 567000, "unit": "هزار تومان"},
    "3345": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 597000, "unit": "هزار تومان"},
    "3752": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 347000, "unit": "هزار تومان"},
    "3356": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 697000, "unit": "هزار تومان"},
    "1209": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 497000, "unit": "هزار تومان"},
    "1208": {"name": "فری سایز - پک 7 عددی رنگ: در تصویر", "price": 397000, "unit": "هزار تومان"},
    "1305": {"name": "فری سایز - پک 4 عددی رنگ: فقط گل قرمز", "price": 517000, "unit": "هزار تومان"},
    "3353": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 417000, "unit": "هزار تومان"},
    "1210": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 657000, "unit": "هزار تومان"},
    "3370": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 697000, "unit": "هزار تومان"},
    "1302": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر با سفید و مشکی دوبل", "price": 497000, "unit": "هزار تومان"},
    "3325": {"name": "فری سایز - پک 4 عددی رنگ: در تصویر", "price": 497000, "unit": "هزار تومان"},
    "3781": {"name": "فری سایز - پک 4 عددی رنگ: مشکی", "price": 397000, "unit": "هزار تومان"},
    "3341": {"name": "فری سایز - پک 6 عددی رنگ: مشکی", "price": 637000, "unit": "هزار تومان"},
    "3379": {"name": "فری سایز - پک 4 عددی رنگ: در تصویر", "price": 697000, "unit": "هزار تومان"},
    "1105": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 737000, "unit": "هزار تومان"},
    "3381": {"name": "فری سایز - پک 4 عددی رنگ: در تصویر (قلاب بافی سبک)", "price": 597000, "unit": "هزار تومان"},
    "3762": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر (جنس پارچه در تصویر رنگبندی)", "price": 697000, "unit": "هزار تومان"},
    "3384": {"name": "فری سایز - پک 6 عددی رنگ: مشکی سبز طوسی", "price": 647000, "unit": "هزار تومان"},
    "1111": {"name": "فری سایز - پک 5 عددی رنگ: در تصویر", "price": 797000, "unit": "هزار تومان"},
    "1306": {"name": "فری سایز - پک 5 عددی رنگ: در تصویر", "price": 597000, "unit": "هزار تومان"},
    "3329": {"name": "فری سایز - پک 5 عددی رنگ: سه رنگ با سفید مشکی دوبل", "price": 557000, "unit": "هزار تومان"},
    "3791": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 597000, "unit": "هزار تومان"},
    "3348": {"name": "فری سایز - پک 8 عددی رنگ: در تصویر", "price": 297000, "unit": "هزار تومان"},
    "3494": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 497000, "unit": "هزار تومان"},
    "3394": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 957000, "unit": "هزار تومان"},
    "1116": {"name": "فری سایز - پک 4 عددی رنگ: در تصویر", "price": 647000, "unit": "هزار تومان"},
    "1112": {"name": "فری سایز - پک 4 عددی رنگ: در تصویر", "price": 597000, "unit": "هزار تومان"},
    "3393": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 597000, "unit": "هزار تومان"},
    "1115": {"name": "فری سایز - پک 6 عددی رنگ: در تصویر", "price": 547000, "unit": "هزار تومان"},
    "1118": {"name": "فری سایز - پک 4 عددی رنگ: در تصویر", "price": 697000, "unit": "هزار تومان"},
}
}

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

@app.route('/')
def index():
    return render_template("index.html", products=products)

@app.route('/order', methods=['POST'])
def order():
    name = request.form.get("name")
    phone = request.form.get("phone")
    address = request.form.get("address")
    order_codes = request.form.getlist("order_code")
    order_counts = request.form.getlist("order_count")

    # فایل PDF
    filename = f"invoice_{phone}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    y_start = height - 2*cm

    c.setFont("Vazir", 16)
    c.drawCentredString(width/2, y_start, reshape_text("🧾 فاکتور سفارش"))
    y = y_start - 2*cm

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

    from reportlab.platypus import Table, TableStyle
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

    c.drawRightString(width - 2*cm, y, reshape_text(f"جمع کل: {total} تومان"))
    c.save()

    # ارسال PDF به مدیر
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    with open(filename, "rb") as f:
        requests.post(url, data={"chat_id": ADMIN_CHAT_ID}, files={"document": f})

    # نمایش PDF به کاربر
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
