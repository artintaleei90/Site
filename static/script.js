document.addEventListener('DOMContentLoaded', () => {
    // اسلایدر حرفه‌ای بدون تصویر
    let slides = document.querySelectorAll('.banner .slide');
    let current = 0;
    function showSlide(index){
        slides.forEach((slide,i)=>{slide.classList.remove('active');});
        slides[index].classList.add('active');
    }
    showSlide(current);
    setInterval(()=>{
        current = (current + 1) % slides.length;
        showSlide(current);
    },5000);
});

// سبد خرید دمو
function addToCart(productName){
    alert(productName + " به سبد خرید اضافه شد!");
}
