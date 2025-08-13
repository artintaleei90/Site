const form = document.getElementById("orderForm");
form.addEventListener("submit", function(e){
    const hiddenDiv = document.getElementById("hiddenInputs");
    hiddenDiv.innerHTML = ""; // پاک کردن قبلی

    document.querySelectorAll(".count").forEach(input => {
        if(input.value > 0){
            hiddenDiv.innerHTML += `<input type="hidden" name="order_code" value="${input.dataset.code}">`;
            hiddenDiv.innerHTML += `<input type="hidden" name="order_count" value="${input.value}">`;
        }
    });
});
