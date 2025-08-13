from flask import Flask, render_template, request, send_file
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import requests
import arabic_reshaper
from bidi.algorithm import get_display
import os

app = Flask(__name__)

# محصولات نمونه
products = {
    "P001": {"name": "مانتو مشکی فری سایز", "price": 697000},
    "P002": {"name": "شومیز سفید", "price": 547000},
    "P003": {"name": "دامن کوتاه", "price": 397000},
}

# اطلاعات مدیر برای ارسال PDF
ADMIN_CHAT_ID = 6933858510
TELEGRAM_TOKEN = "7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE"

# ثبت فونت فارسی
pdfmetrics.registerFont(TTFont('Vazirmatn', 'https://github.com/rastikerdar/vazir-font/raw/master/Vazirmatn-Regular.ttf'))

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

    # ساخت PDF
    filename = f"invoice_{phone}.pdf"
    c = canvas.Canvas(filename)
    y = 800

    c.setFont("Vazirmatn", 14)
    c.drawString(50, y, reshape_text(f"سفارش مشتری: {name}"))
    y -= 30
    c.drawString(50, y, reshape_text(f"شماره تماس: {phone}"))
    y -= 30
    c.drawString(50, y, reshape_text(f"آدرس: {address}"))
    y -= 50
    c.drawString(50, y, reshape_text("محصولات:"))
    y -= 30

    total = 0
    for code, count in zip(order_codes, order_counts):
        count = int(count)
        product = products.get(code)
        if product:
            price = product["price"]
            line = f"{product['name']} - تعداد: {count} - قیمت واحد: {price}"
            c.drawString(60, y, reshape_text(line))
            total += count * price
            y -= 20

    c.drawString(50, y-20, reshape_text(f"جمع کل: {total} تومان"))
    c.save()

    # ارسال PDF به مدیر
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    with open(filename, "rb") as f:
        requests.post(url, data={"chat_id": ADMIN_CHAT_ID}, files={"document": f})

    # نمایش PDF به کاربر
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)