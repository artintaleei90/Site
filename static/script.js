const telegramBotToken = "توکن_ربات_تو";
const adminChatId = "آیدی_مدیر";

let cart = [];
let currentFilter = 'all';

// نمونه محصولات
const products = [
    { id: 1, name: "پیراهن مردانه", category: "لباس", price: 350000 },
    { id: 2, name: "کفش اسپرت", category: "کفش", price: 450000 },
    { id: 3, name: "کلاه اسپرت", category: "اکسسوری", price: 90000 },
];

// نمایش محصولات
function displayProducts() {
    const container = document.getElementById('products-container');
    container.innerHTML = '';
    const filtered = currentFilter === 'all' ? products : products.filter(p => p.category === currentFilter);

    filtered.forEach(p => {
        const card = document.createElement('div');
        card.className = 'product-card';
        card.innerHTML = `
            <h3>${p.name}</h3>
            <p>${p.price.toLocaleString()} تومان</p>
            <button onclick="addToCart(${p.id})">افزودن به سبد</button>
        `;
        container.appendChild(card);
    });
}

// افزودن به سبد خرید
function addToCart(productId) {
    const product = products.find(p => p.id === productId);
    const exist = cart.find(item => item.id === productId);

    if (exist) {
        exist.quantity++;
    } else {
        cart.push({...product, quantity: 1});
    }
    updateCart();
}

// بروزرسانی سبد خرید
function updateCart() {
    const cartItems = document.getElementById('cart-items');
    cartItems.innerHTML = '';
    let total = 0;

    cart.forEach(item => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.name}</td>
            <td>${item.quantity}</td>
            <td>${itemTotal.toLocaleString()}</td>
        `;
        cartItems.appendChild(row);
    });

    document.getElementById('cart-total').textContent = total.toLocaleString();
    document.getElementById('cart-count').textContent = cart.reduce((sum,i)=>sum+i.quantity,0);
}

// مدیریت نمایش سبد خرید
function toggleCart() {
    document.getElementById('cart-popup').classList.toggle('active');
    document.getElementById('overlay').classList.toggle('active');
}

function closeCart() {
    document.getElementById('cart-popup').classList.remove('active');
    document.getElementById('overlay').classList.remove('active');
}

// مودال اطلاعات مشتری
function showUserInfoModal() {
    document.getElementById('user-info-modal').classList.add('active');
    document.getElementById('overlay').classList.add('active');
    closeCart();
}

function closeUserInfoModal() {
    document.getElementById('user-info-modal').classList.remove('active');
    document.getElementById('overlay').classList.remove('active');
}

// تولید فاکتور و ارسال به تلگرام
function generateInvoice() {
    const name = document.getElementById('name').value;
    const phone = document.getElementById('phone').value;
    const address = document.getElementById('address').value;

    if(!name||!phone||!address){ alert("لطفا همه فیلدها را پر کنید"); return;}

    closeUserInfoModal();

    document.getElementById('invoice-name').textContent = name;
    document.getElementById('invoice-phone').textContent = phone;
    document.getElementById('invoice-address').textContent = address;

    const invoiceBody = document.getElementById('invoice-items-body');
    invoiceBody.innerHTML = '';
    let total = 0;

    cart.forEach(item => {
        const row = document.createElement('tr');
        const itemTotal = item.price * item.quantity;
        total += itemTotal;
        row.innerHTML = `<td>${item.name}</td><td>${item.quantity}</td><td>${itemTotal.toLocaleString()}</td>`;
        invoiceBody.appendChild(row);
    });

    document.getElementById('invoice-total').textContent = total.toLocaleString();
    document.getElementById('invoice-modal').classList.add('active');
    document.getElementById('overlay').classList.add('active');

    sendToTelegram(name, phone, address, total);
}

// بستن مودال فاکتور
function closeInvoice() {
    document.getElementById('invoice-modal').classList.remove('active');
    document.getElementById('overlay').classList.remove('active');
}

// چاپ فاکتور
function printInvoice() {
    const invoiceContent = document.getElementById('invoice-modal').innerHTML;
    const originalContent = document.body.innerHTML;
    document.body.innerHTML = invoiceContent;
    window.print();
    document.body.innerHTML = originalContent;
    displayProducts();
}

// ارسال به تلگرام
function sendToTelegram(name, phone, address, total){
    let text = `فاکتور خرید از هالستون\nنام: ${name}\nشماره: ${phone}\nآدرس: ${address}\n\nمحصولات:\n`;
    cart.forEach(item => { text += `${item.name} - ${item.quantity} عدد - ${(item.price*item.quantity).toLocaleString()} تومان\n` });
    text += `\nجمع کل: ${total.toLocaleString()} تومان`;

    fetch(`https://api.telegram.org/bot${telegramBotToken}/sendMessage`, {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({chat_id:adminChatId,text:text})
    }).then(r=>r.json()).then(d=>{if(d.ok){alert('فاکتور با موفقیت ارسال شد');} else {alert('ارسال با خطا مواجه شد');}});
}

// فیلتر محصولات
function filterProducts(category){ currentFilter=category; displayProducts(); document.getElementById('categories-menu').classList.remove('active'); }
function showAllProducts(){ filterProducts('all'); }
function toggleCategories(){ document.getElementById('categories-menu').classList.toggle('active'); }
function closeAllModals(){
    ['cart-popup','user-info-modal','invoice-modal','overlay','categories-menu'].forEach(id=>{
        document.getElementById(id).classList.remove('active');
    });
}

document.addEventListener('DOMContentLoaded',()=>{ displayProducts(); document.addEventListener('keydown',e=>{ if(e.key==='Escape') closeAllModals(); }); });
