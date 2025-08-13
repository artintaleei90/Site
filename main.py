from flask import Flask, render_template, request
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os
import requests

app = Flask(__name__)
os.makedirs("orders", exist_ok=True)

# محصولات نمونه
products = {
    "P001": {"name": "مانتو مشکی فری سایز", "price": 697000},
    "P002": {"name": "شومیز سفید", "price": 547000},
    "P003": {"name": "دامن کوتاه", "price": 397000},
}

# اطلاعات مدیر تلگرام
ADMIN_CHAT_ID = 6933858510
TELEGRAM_TOKEN = "7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE"

def create_invoice(filename, customer, order_items):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    y = height - 50

    # عنوان فاکتور
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, y, "فاکتور سفارش")
    y -= 40

    c.setFont("Helvetica", 12)
    # اطلاعات مشتری
    c.drawString(50, y, f"نام مشتری: {customer['name']}")
    y -= 20
    c.drawString(50, y, f"شماره تماس: {customer['phone']}")
    y -= 20
    c.drawString(50, y, f"آدرس: {customer['address']}")
    y -= 30

    # خط جداکننده
    c.line(50, y, width - 50, y)
    y -= 20

    total = 0
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "محصولات:")
    y -= 20
    c.setFont("Helvetica", 12)

    for item in order_items:
        product = products.get(item["code"])
        if product:
            line = f"{product['name']} - تعداد: {item['count']} - قیمت واحد: {product['price']} تومان"
            c.drawString(60, y, line)
            total += product['price'] * item['count']
            y -= 20

    # خط جداکننده جمع کل
    y -= 10
    c.line(50, y, width - 50, y)
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, f"جمع کل: {total} تومان")

    c.save()

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

    order_items = [{"code": c, "count": int(n)} for c, n in zip(order_codes, order_counts)]

    filename = f"orders/invoice_{phone}.pdf"
    customer = {"name": name, "phone": phone, "address": address}
    create_invoice(filename, customer, order_items)

    # ارسال به تلگرام
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    with open(filename, "rb") as f:
        requests.post(url, data={"chat_id": ADMIN_CHAT_ID}, files={"document": f})

    # پاک کردن فایل بعد از ارسال
    os.remove(filename)

    return "✅ سفارش ثبت شد و فاکتور برای مدیر ارسال شد!"

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)