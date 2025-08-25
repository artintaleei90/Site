let cart = [];
const cartCount = document.getElementById("cart-count");
const miniCart = document.getElementById("mini-cart");
const miniCartItems = document.getElementById("mini-cart-items");

// افزودن محصول به سبد خرید
function addToCart(name, price, image) {
    const existing = cart.find(item => item.name === name);
    if (existing) {
        existing.quantity++;
    } else {
        cart.push({ name, price, image, quantity: 1 });
    }
    updateCart();
}

// آپدیت تعداد و نمایش سبد
function updateCart() {
    cartCount.textContent = cart.reduce((sum, item) => sum + item.quantity, 0);

    // نمایش آیتم‌ها در مینی کارت
    miniCartItems.innerHTML = "";
    cart.forEach(item => {
        const div = document.createElement("div");
        div.classList.add("mini-cart-item");
        div.innerHTML = `
            <img src="${item.image}" alt="${item.name}">
            <div>
                <p>${item.name}</p>
                <span>${item.quantity} عدد</span>
            </div>
        `;
        miniCartItems.appendChild(div);
    });

    // بازکردن مینی کارت
    miniCart.classList.remove("hidden");
}

// رفتن به صفحه جزئیات محصول
function viewProduct(productId) {
    window.location.href = `/product.html?id=${productId}`;
}

// بستن مینی کارت با کلیک بیرون
document.addEventListener("click", (e) => {
    if (!miniCart.contains(e.target) && !e.target.classList.contains("add-to-cart")) {
        miniCart.classList.add("hidden");
    }
});
