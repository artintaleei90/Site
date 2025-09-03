from flask import Flask, jsonify, request, send_file, render_template_string
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import telebot

app = Flask(__name__)

# توکن ربات تلگرام
BOT_TOKEN = "7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE"
ADMIN_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"  # آیدی عددی ادمین
bot = telebot.TeleBot(BOT_TOKEN)

# دیتابیس محصولات
products = {
    "1107": {
        "category": "women",
        "image": "https://raw.githubusercontent.com/artintaleei90/Site/main/IMG_0395.jpeg",
        "name": "فری سایز - پک 6 عددی رنگ: سفید و مشکی",
        "price": 547000
    },
    "3390": {
        "category": "women",
        "image": "https://raw.githubusercontent.com/artintaleei90/Site/main/IMG_0394.jpeg",
        "name": "فری سایز - پک 6 عددی رنگ: در تصویر",
        "price": 697000
    }
}

# API محصولات
@app.route("/api/products")
def api_products():
    return jsonify(products)

# تولید فاکتور و ارسال PDF
@app.route("/invoice", methods=["GET"])
def invoice():
    try:
        # دریافت اطلاعات مشتری از URL
        name = request.args.get("name")
        phone = request.args.get("phone")
        city = request.args.get("city")
        address = request.args.get("address")
        cart = request.args.get("cart")

        if not name or not phone or not address:
            return "اطلاعات ناقص است!", 400

        # تبدیل سبد خرید از JSON
        import json
        cart = json.loads(cart) if cart else {}

        # ساخت PDF در حافظه
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Farsi', fontName='Helvetica', fontSize=12, alignment=1))

        story = []
        story.append(Paragraph("فاکتور خرید", styles['Title']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"نام مشتری: {name}", styles['Farsi']))
        story.append(Paragraph(f"شماره تماس: {phone}", styles['Farsi']))
        story.append(Paragraph(f"شهر: {city}", styles['Farsi']))
        story.append(Paragraph(f"آدرس: {address}", styles['Farsi']))
        story.append(Spacer(1, 12))

        # جدول محصولات
        table_data = [["نام محصول", "تعداد", "قیمت واحد", "قیمت کل"]]
        total = 0
        for code, qty in cart.items():
            product = products.get(code, {})
            pname = product.get("name", "نامشخص")
            price = product.get("price", 0)
            subtotal = qty * price
            total += subtotal
            table_data.append([pname, qty, f"{price:,} تومان", f"{subtotal:,} تومان"])

        table_data.append(["", "", "جمع کل", f"{total:,} تومان"])
        table = Table(table_data, colWidths=[200, 50, 100, 100])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("ALIGN", (1, 1), (-1, -1), "CENTER")
        ]))
        story.append(table)

        doc.build(story)
        buffer.seek(0)

        # ارسال PDF به تلگرام
        bot.send_document(ADMIN_CHAT_ID, buffer, visible_file_name="invoice.pdf")

        buffer.seek(0)
        return send_file(buffer, as_attachment=False, download_name="invoice.pdf", mimetype="application/pdf")
    except Exception as e:
        return f"خطا در ساخت فاکتور: {e}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
