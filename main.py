from flask import Flask, render_template, request
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import requests
import os
import arabic_reshaper
from bidi.algorithm import get_display

app = Flask(__name__)
os.makedirs("orders", exist_ok=True)

# محصولات نمونه
products = {
    "P001": {"name": "مانتو مشکی فری سایز", "price": 697000, "img": "/static/img/manto.jpg"},
    "P002": {"name": "شومیز سفید", "price": 547000, "img": "/static/img/shomiz.jpg"},
    "P003": {"name": "دامن کوتاه", "price": 397000, "img": "/static/img/daman.jpg"},
}

# اطلاعات مدیر برای ارسال PDF
ADMIN_CHAT_ID = 6933858510
TELEGRAM_TOKEN = "7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE"

# ثبت فونت فارسی
pdfmetrics.registerFont(TTFont('Vazirmatn', 'fonts/Vazirmatn-Regular.ttf'))

# تابع برای درست کردن متن فارسی (چسبیده و راست‌چین)
def to_persian(text):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

@app.route("/", methods=["GET", "POST"])
def index():
    reversed_text = ""
    if request.method == "POST" and "reverse_input" in request.form:
        text = request.form.get("reverse_input")
        reversed_text = text[::-1]  # برعکس کردن متن
    return render_template("index.html", products=products, reversed_text=reversed_text)

@app.route('/order', methods=['POST'])
def order():
    name = request.form.get("name")
    phone = request.form.get("phone")
    city = request.form.get("city")
    address = request.form.get("address")
    order_codes = request.form.getlist("order_code")
    order_counts = request.form.getlist("order_count")

    # ساخت PDF فاکتور
    filename = f"orders/invoice_{phone}.pdf"
    c = canvas.Canvas(filename)
    c.setFont("Vazirmatn", 14)
    y = 800

    # نوشتن متن فارسی و راست‌چین
    c.drawRightString(550, y, to_persian(f"سفارش مشتری: {name}"))
    y -= 30
    c.drawRightString(550, y, to_persian(f"شماره تماس: {phone}"))
    y -= 30
    c.drawRightString(550, y, to_persian(f"شهر: {city}, آدرس: {address}"))
    y -= 50
    c.drawRightString(550, y, to_persian("محصولات:"))
    y -= 30

    total = 0
    for code, count in zip(order_codes, order_counts):
        count = int(count)
        product = products.get(code)
        if product:
            price = product["price"]
            c.drawRightString(550, y, to_persian(f"{product['name']} - تعداد: {count} - قیمت واحد: {price} تومان"))
            total += count * price
            y -= 20

    c.drawRightString(550, y-20, to_persian(f"جمع کل: {total} تومان"))
    c.save()

    # ارسال PDF به مدیر تلگرام
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    with open(filename, "rb") as f:
        requests.post(url, data={"chat_id": ADMIN_CHAT_ID}, files={"document": f})

    # پاک کردن فایل بعد از ارسال
    os.remove(filename)

    return f"✅ سفارش ثبت شد و فاکتور برای مدیر ارسال شد!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
