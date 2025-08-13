from flask import Flask, render_template, request
from reportlab.pdfgen import canvas
import requests

app = Flask(__name__)

# محصولات نمونه
products = {
    "P001": {"name": "مانتو مشکی فری سایز", "price": 697000},
    "P002": {"name": "شومیز سفید", "price": 547000},
    "P003": {"name": "دامن کوتاه", "price": 397000},
}

# اطلاعات مدیر برای ارسال PDF
ADMIN_CHAT_ID = 6933858510  # Chat ID مدیر
TELEGRAM_TOKEN = "7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE"

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
    filename = f"invoice_{phone}.pdf"
    c = canvas.Canvas(filename)
    y = 800
    c.drawString(50, y, f"سفارش مشتری: {name}")
    y -= 30
    c.drawString(50, y, f"شماره تماس: {phone}")
    y -= 30
    c.drawString(50, y, f"شهر: {city}, آدرس: {address}")
    y -= 50
    c.drawString(50, y, "محصولات:")
    y -= 30

    total = 0
    for code, count in zip(order_codes, order_counts):
        count = int(count)
        product = products.get(code)
        if product:
            price = product["price"]
            c.drawString(60, y, f"{product['name']} - تعداد: {count} - قیمت واحد: {price}")
            total += count * price
            y -= 20

    c.drawString(50, y-20, f"جمع کل: {total} تومان")
    c.save()

    # ارسال PDF به مدیر از طریق Telegram
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    with open(filename, "rb") as f:
        requests.post(url, data={"chat_id": ADMIN_CHAT_ID}, files={"document": f})

    return f"✅ سفارش ثبت شد و فاکتور برای مدیر ارسال شد!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
