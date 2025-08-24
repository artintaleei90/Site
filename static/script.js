// اسلایدر اتوماتیک
let slides = document.querySelectorAll('.hero-slider .slide');
let currentSlide = 0;
function showSlide(index) {
    slides.forEach(slide => slide.classList.remove('active'));
    slides[index].classList.add('active');
}
setInterval(() => {
    currentSlide = (currentSlide + 1) % slides.length;
    showSlide(currentSlide);
}, 5000);

// محصولات دمو
const products = [
    { id:1, name:"مانتو تابستانه", price:"750,000 تومان", img:"images/product1.jpg" },
    { id:2, name:"شومیز حریر", price:"420,000 تومان", img:"images/product2.jpg" },
    { id:3, name:"ست راحتی", price:"580,000 تومان", img:"images/product3.jpg" },
    { id:4, name:"شلوار کتان", price:"350,000 تومان", img:"images/product4.jpg" }
];

const productsContainer = document.getElementById('products');
products.forEach(product=>{
    const card = document.createElement('div');
    card.classList.add('product-card');
    card.innerHTML = `
        <img src="${product.img}" alt="${product.name}">
        <h3>${product.name}</h3>
        <div class="price">${product.price}</div>
        <button class="add-to-cart" onclick="addToCart('${product.name}')">افزودن به سبد</button>
    `;
    productsContainer.appendChild(card);
});

// افزودن به سبد خرید
function addToCart(productName) {
    alert(`محصول "${productName}" به سبد خرید اضافه شد ✅`);
}

// عضویت در خبرنامه
document.getElementById('newsletter-form').addEventListener('submit', function(e){
    e.preventDefault();
    alert("عضویت شما با موفقیت انجام شد ✅");
});
