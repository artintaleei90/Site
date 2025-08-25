/* Halston — client cart (بدون عکس) */
/* سبد در localStorage ذخیره می‌شود تا بین صفحات حفظ شود */

const STORAGE_KEY = "halston_cart_v1";

/* بارگذاری سبد از localStorage */
function loadCart() {
  const raw = localStorage.getItem(STORAGE_KEY);
  return raw ? JSON.parse(raw) : [];
}

/* ذخیره سبد */
function saveCart(cart) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(cart));
}

/* افزودن محصول به سبد (تعداد 1 اضافه می‌شود) */
function addToCart(id, name, price) {
  const cart = loadCart();
  const idx = cart.findIndex(item => item.id === id);
  if (idx > -1) {
    cart[idx].quantity += 1;
  } else {
    cart.push({ id: id, name: name, price: price, quantity: 1 });
  }
  saveCart(cart);
  updateCartUI();
  openCartPopup();
}

/* کاهش یا افزایش تعداد */
function changeQty(id, delta) {
  const cart = loadCart();
  const idx = cart.findIndex(i => i.id === id);
  if (idx === -1) return;
  cart[idx].quantity += delta;
  if (cart[idx].quantity <= 0) {
    cart.splice(idx, 1);
  }
  saveCart(cart);
  updateCartUI();
}

/* پاک کردن کامل سبد */
function clearCart() {
  localStorage.removeItem(STORAGE_KEY);
  updateCartUI();
}

/* نمایش سبد (مینی‌کارت) */
function updateCartUI() {
  const cart = loadCart();
  const countEl = document.getElementById("cart-count");
  const itemsEl = document.getElementById("cart-items");
  const totalEl = document.getElementById("cart-total");

  if (countEl) countEl.textContent = cart.reduce((s, i) => s + i.quantity, 0);

  if (itemsEl) {
    itemsEl.innerHTML = "";
    if (cart.length === 0) {
      itemsEl.innerHTML = "<div style='padding:10px;color:#666'>سبد خرید خالی است.</div>";
    } else {
      cart.forEach(item => {
        const div = document.createElement("div");
        div.className = "cart-item";
        div.innerHTML = `
          <div class="left">
            <strong>${item.name}</strong>
            <div style="font-size:13px;color:#666">${item.price.toLocaleString()} تومان</div>
          </div>
          <div class="qty-controls">
            <button onclick="changeQty(${item.id}, -1)">−</button>
            <div style="min-width:28px;text-align:center">${item.quantity}</div>
            <button onclick="changeQty(${item.id}, 1)">+</button>
          </div>
        `;
        itemsEl.appendChild(div);
      });
    }
  }

  if (totalEl) {
    const total = cart.reduce((s, i) => s + i.price * i.quantity, 0);
    totalEl.textContent = "جمع: " + total.toLocaleString() + " تومان";
  }
}

/* باز/بستن پاپ‌آپ */
function toggleCartPopup(e) {
  e && e.stopPropagation();
  const popup = document.getElementById("cart-popup");
  if (!popup) return;
  popup.classList.toggle("hidden");
}

/* باز کردن (وقتی محصول اضافه میشه) */
function openCartPopup() {
  const popup = document.getElementById("cart-popup");
  if (!popup) return;
  popup.classList.remove("hidden");
}

/* بستن با کلیک بیرون */
document.addEventListener("click", (e) => {
  const popup = document.getElementById("cart-popup");
  const btn = document.querySelector(".cart-btn");
  if (!popup) return;
  if (popup.classList.contains("hidden")) return;
  // اگر روی popup یا دکمه کلیک نشده بود، ببند
  if (!popup.contains(e.target) && (!btn || !btn.contains(e.target))) {
    popup.classList.add("hidden");
  }
});

/* رفتن به صفحه جزئیات */
function goToProduct(id) {
  window.location.href = `/product/${id}`;
}

/* تسویه — اینجا میتونی به سرور ارسال کنی */
function checkout() {
  const cart = loadCart();
  if (cart.length === 0) {
    alert("سبد خرید خالی است.");
    return;
  }
  // برای نمونه فقط نمایش میدیم؛ تو میتونی AJAX بزنی به سرور
  let summary = cart.map(i => `${i.name} x${i.quantity}`).join("\n");
  alert("سفارش ثبت شد:\n" + summary);
  clearCart();
}

/* مقداردهی اولیه در لود صفحه */
document.addEventListener("DOMContentLoaded", () => {
  updateCartUI();
});
