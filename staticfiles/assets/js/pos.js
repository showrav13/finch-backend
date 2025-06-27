function getCSRFToken2() {
    let csrfToken = null;
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        let [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            csrfToken = value;
        }
    }
    return csrfToken;
}

var selectedColor = "";
var selectedSize = "";
var lastSelectedProduct = null; // Track last selected product ID
let cart = loadCart();

// Function to handle color selection
function addColor(element) {
    selectedColor = element.getAttribute("data-color");
    var newImageUrl = element.getAttribute('data-image-url');
    
    var productImage = document.getElementById('product-image-' + element.getAttribute('data-product-id'));
    if (productImage) {
        productImage.src = newImageUrl;
    }
}

// Function to handle size selection
function addSize(selectElement) {
    selectedSize = selectElement.value;
}

function addToCart(id, name, price, sku, in_stock) {
    if (selectedColor === "" || selectedSize === "") {
        showAlert("Please select both a color and a size before adding to the cart.", "danger");
        return;
    }

    fetch("/pos/verify_product_size_color/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken2()
        },
        body: JSON.stringify({
            product_id: id,
            color: selectedColor,
            size: selectedSize,
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.valid) {
            if (lastSelectedProduct === null) {
                lastSelectedProduct = id;
            }

            const existingItem = cart.find(item => 
                item.id === id && 
                item.color === selectedColor && 
                item.size === selectedSize
            );

            if (existingItem) {
                showAlert("Already in cart!", "danger");
                // existingItem.quantity += 1; 
            } else {
                showAlert("New item, adding to cart.", "success");
                cart.unshift({
                    id,
                    name,
                    price,
                    color: selectedColor,
                    size: selectedSize,
                    quantity: 1,
                    sku
                });
            }

            saveCart();

            updateCart();
            // showAlert("Product added to cart successfully.", "success");
        } else {
            showAlert(data.error, "danger");
        }
    })
    .catch(error => {
        showAlert(error, "danger");
    });
}
function showAlert(message, type) {
    const alertContainer = document.querySelector('.container-fluid');
    const alert = document.createElement('div');
    alert.classList.add('alert', `alert-${type}`, 'alert-icon', 'fade', 'show');
    alert.role = 'alert';
    alert.innerHTML = `
        <div class="d-flex align-items-center">
            <div class="avatar-sm rounded bg-${type} d-flex justify-content-center align-items-center fs-18 me-2 flex-shrink-0">
                <i class="bx ${type === 'danger' ? 'bx-x-circle' : type === 'success' ? 'bx-check-circle' : 'bx-info-circle'} text-white"></i>
            </div>
            <div class="flex-grow-1">
                ${message}
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    alertContainer.appendChild(alert);

    // Remove alert after 1 second
    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => alert.remove(), 500); // Wait for fade-out transition
    }, 1000);
}

async function verifyProductStock(id, color) {
    try {
        const response = await fetch("/pos/verify_product_stock/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken2()
            },
            body: JSON.stringify({ product_id: id, color: color }),
        });

        const data = await response.json();

        if (data.valid) {
            return data.stock;
        } else {
            return 0;
        }
    } catch (error) {
        showAlert(error, "danger");
        return 0;
    }
}

// Load cart from localStorage if available
function loadCart() {
    const storedCart = localStorage.getItem('cart');
    return storedCart ? JSON.parse(storedCart) : [];
}

// Save cart to localStorage
function saveCart() {
    localStorage.setItem('cart', JSON.stringify(cart));
}

function updateCart() {
    let cartHtml = '';
    let totalPrice = 0;

    if (cart.length === 0) {
        cartHtml = `
            <div class="text-center text-muted py-3">
                <i class="fa fa-shopping-cart fa-2x mb-2"></i>
                <p>Your cart is empty</p>
            </div>
        `;
    } else {    
        cart.forEach((item, index) => {
        totalPrice += item.price * item.quantity;
        cartHtml += `
            <div class="cart-item d-flex justify-content-between align-items-center mb-1 p-2 rounded-lg shadow-sm bg-white">
                <!-- Item Details -->
                <div class="item-details w-3/12 pe-3">
                    <div><strong class="fs-7 text-dark">${item.name}</strong></div>
                    <div class="text-muted d-flex align-items-center">
                        <span class="text-primary">${item.size}</span>
                        <span data-color="${item.color}" 
                            class="color-circle border rounded-circle ms-1" 
                            style="background-color: ${item.color}; width: 18px; height: 18px; display: inline-block; cursor: pointer;">
                        </span>
                    </div>
                    <div class="text-muted">SKU: <span class="text-primary">${item.sku}</span></div>
                </div>

                <!-- Price Column -->
                <div class="item-price text-center w-2/12">
                    <div class="fw-bold fs-7 text-dark">$ ${item.price.toFixed(2)}</div>
                </div>

                <!-- Multiplication Symbol -->
                <div class="item-multiply text-center w-1/12">
                    <div class="fs-7 text-dark">×</div>
                </div>

                <!-- Item Quantity -->
                <div class="item-quantity d-flex align-items-center justify-content-center w-3/12">
                    <input type="number" id="quantity-${index}" value="${item.quantity}" min="1" class="custom-quantity-input mx-2 text-center h-8 text-sm border border-gray-300 rounded-md p-1 bg-gray-50 focus:ring-2 focus:ring-blue-500 transition-all" onchange="updateQuantity(${index}, 0, this.value)" style="width: 3rem;" />
                </div>

                <!-- Subtotal Column -->
                <div class="item-subtotal text-center w-2/12">
                    <div class="fw-bold fs-7 text-dark">$ ${(item.price * item.quantity).toFixed(2)}</div>
                </div>

                <!-- Delete Button Column -->
                <div class="item-delete text-end w-1/12 ps-3">
                    <button class="btn btn-xs btn-danger ms-2 mt-1" onclick="removeItem(${index})">
                        <i class="fa fa-trash"></i> <!-- Font Awesome Trash Icon -->
                    </button>
                </div>
            </div>
        `;
        });
    }
    

    document.getElementById('cartItems').innerHTML = cartHtml;
    document.getElementById('subtotal').innerText = totalPrice.toFixed(2);
    var taxAmount = (totalPrice * TAX_RATE) / 100;
    document.getElementById('taxAmount').innerText = taxAmount.toFixed(2);
    const finalTotal = totalPrice + taxAmount;
    document.getElementById('totalPrice').innerText = finalTotal.toFixed(2);
    document.getElementById('totalAmount').value = finalTotal.toFixed(2);  // Add this line // Add this line
}

// Update quantity (minus, plus, or manual input change)
async function updateQuantity(index, change, newQuantity) {
    const stock = await verifyProductStock(cart[index].id, cart[index].color);
    quantity_input = document.getElementById(`quantity-${index}`);

    if (stock === 0) {
        showAlert("This color is out of stock.", "danger");
        quantity_input.value = newQuantity - 1;
        return;
    }

    if (newQuantity && newQuantity > stock) {
        showAlert("This color is out of stock.", "danger");
        quantity_input.value = newQuantity - 1;
        return;
    }

    if (change !== 0) {
        if (cart[index].quantity + change > stock) {
            showAlert("This color is out of stock.", "danger");
            return;
        }
        cart[index].quantity += change;
    } else if (newQuantity && newQuantity > 0) {
        cart[index].quantity = Math.min(parseInt(newQuantity), stock); // Prevent exceeding stock
    }

    if (cart[index].quantity < 1) {
        cart[index].quantity = 1; // Prevent going below 1
    }

    saveCart();
    updateCart();
}

// Remove item from cart
function removeItem(index) {
    cart.splice(index, 1); // Remove item at the given index
    saveCart(); // Save the cart after removal
    updateCart();
}

// checkokut with data (User, Total amount, Discount, Tax, Payment method, Notes, Cart)



function checkout(){
    customer = document.getElementById("customerSelect").value;
    paymentMethod = document.getElementById("paymentMethod").value;
    totalAmount = document.getElementById("totalAmount").value;
    totalPaid = document.getElementById("paidAmount").value;
    note = document.getElementById("note").value;
    console.log(cart);
    console.log(totalAmount);
    console.log(paymentMethod);
    console.log(note);
    console.log(cart)
    // make a post request to the checkout view
    fetch("/pos/checkout/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken2()
        },
        body: JSON.stringify({cart: cart, totalAmount: totalAmount, paymentMethod: paymentMethod, note: note, customer: customer, totalPaid: totalPaid}),
    })
    .then(response => response.json())
    .then(data => {
        if (data.valid) {
            showAlert("Purchase successful", "success");
            cart = [];
            saveCart();
            updateCart();
            // Generate Invoice
            window.open(`/pos/invoice/${data.pos_id}`, "_blank");
            // reload the page
            location.reload();
        } else {
            showAlert(data.error, "danger");
        }
    });
}

// Initial cart update
updateCart();
