let cart = [];

function addToCart(name, price) {
    cart.push({ name, price });
    document.getElementById("cart-count").innerText = cart.length;
    updateCart();
    document.getElementById("cart-popup").style.display = "block";
}

function updateCart() {
    const cartItems = document.getElementById("cart-items");
    cartItems.innerHTML = "";
    cart.forEach(item => {
        const li = document.createElement("li");
        li.textContent = `${item.name} - ${item.price} تومان`;
        cartItems.appendChild(li);
    });
}

function toggleCart() {
    const cartPopup = document.getElementById("cart-popup");
    cartPopup.style.display = cartPopup.style.display === "block" ? "none" : "block";
}

function closeCart() {
    document.getElementById("cart-popup").style.display = "none";
}
