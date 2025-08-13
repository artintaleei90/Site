from flask import Flask, render_template, request
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import requests
import os

app = Flask(__name__)
os.makedirs("orders", exist_ok=True)

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
pdfmetrics.registerFont(TTFont('Vazirmatn', 'Vazirmatn-Regular.ttf'))

@app.route('/')
def index():
    return render_template("index.html", products=products)

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

    c.drawRightString(550, y, f"سفارش مشتری: {name}")
    y -= 30
    c.drawRightString(550, y, f"شماره تماس: {phone}")
    y -= 30
    c.drawRightString(550, y, f"شهر: {city}, آدرس: {address}")
    y -= 50
    c.drawRightString(550, y, "محصولات:")
    y -= 30

    total = 0
    for code, count in zip(order_codes, order_counts):
        count = int(count)
        product = products.get(code)
        if product:
            price = product["price"]
            c.drawRightString(550, y, f"{product['name']} - تعداد: {count} - قیمت واحد: {price} تومان")
            total += count * price
            y -= 20

    c.drawRightString(550, y-20, f"جمع کل: {total} تومان")
    c.save()

    # ارسال PDF به مدیر از طریق Telegram
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    with open(filename, "rb") as f:
        requests.post(url, data={"chat_id": ADMIN_CHAT_ID}, files={"document": f})

    # پاک کردن فایل بعد از ارسال
    os.remove(filename)

    return f"✅ سفارش ثبت شد و فاکتور برای مدیر ارسال شد!"


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
