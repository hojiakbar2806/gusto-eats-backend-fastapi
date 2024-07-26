// Global variables
let cartItems = []; // Array to store selected products
let totalPrice = 0; // Total price accumulator
let cartQuantity = 0; // Cart quantity counter

// Function to initialize the page
function initPage() {
  // Initialize Telegram script
  initTelegramScript();

  // Check and update button states for products in the cart
  cartItems = JSON.parse(localStorage.getItem("cartItems")) || [];
  cartItems.forEach((item) => {
    const button = document.getElementById(`cart_button-${item.id}`);
    if (button) {
      button.innerText = "Delete";
      button.style.backgroundColor = "red";
    }
  });
}

// Function to initialize Telegram script
function initTelegramScript() {
  let tg = window.Telegram.WebApp;

  // Initialize Telegram WebApp
  tg.ready();
  tg.expand();

  // Define main button properties
  tg.MainButton.textColor = "#FFFFFF";
  tg.MainButton.color = "#008000";
  tg.MainButton.setText("Order");

  function showMainButton() {
    if (cartItems.length > 0) {
      tg.MainButton.show();
    } else {
      tg.MainButton.hide();
    }
  }

  // Retrieve stored items from localStorage on page load
  if (localStorage.getItem("cartItems")) {
    cartItems = JSON.parse(localStorage.getItem("cartItems"));
    updateCart(); // Update cart on page load
  }

  // Function to add product to cart
window.addToCart = function (productJson) {
    const product = JSON.parse(productJson);  // Parse JSON string to an object
    const existingItem = cartItems.find((item) => item.id === product.id);
    const button = document.getElementById(`cart_button-${product.id}`);

    if (existingItem) {
        // Remove the item from the cart
        cartItems = cartItems.filter((item) => item.id !== product.id);
        button.innerText = "Add to cart";
        button.style.backgroundColor = "#1677ff";
    } else {
        // Add the item to the cart
        cartItems.push({
            id: product.id,
            name: product.name,
            image: product.image,
            file_id: product.telegram_file_id,
            price: product.price,
            discount: product.discount,
            quantity: 1,
        });
        button.innerText = "Delete";
        button.style.backgroundColor = "red";
    }
    updateCart(); // Update cart display
    updateLocalStorage();
    showMainButton(); // Update main button visibility
};


  // Function to update cart display
  function updateCart() {
    cartQuantity = cartItems.reduce((total, item) => total + item.quantity, 0);
    document.getElementById("cartQuantity").textContent =
      cartQuantity.toString();

    // Calculate total price
    totalPrice = cartItems.reduce(
      (total, item) => total + item.price * item.quantity,
      0
    );
    console.log("Total Price:", totalPrice);
  }

  // Function to update localStorage
  function updateLocalStorage() {
    localStorage.setItem("cartItems", JSON.stringify(cartItems));
    localStorage.setItem("totalPrice", totalPrice.toFixed(2));
  }

  // Function to open cart modal
  window.openCartModal = function () {
    updateCartModal();
    document.getElementById("cartModal").style.top = "0";
  };

  // Function to close cart modal
  window.closeCartModal = function () {
    document.getElementById("cartModal").style.top = "-200%";
  };

  // Function to update cart modal display
  function updateCartModal() {
    const cartList = document.getElementById("tbody");
    cartList.innerHTML = ""; // Clear previous list

    // Populate cart items
    cartItems.forEach((item) => {
      cartList.innerHTML += `
        <tr>
          <td><img height="60px" src="${item.image}" alt="${item.name}"/></td>
          <td>${item.name}</td>
          <td>${item.quantity}</td>
          <td>${item.price * item.quantity}</td>
        </tr>`;
    });

    // Update total price display
    document.getElementById("totalPriceDisplay").textContent =
      totalPrice.toFixed(2);
  }

  // Function to clear cart
  window.clearCart = function () {
    cartItems.forEach((item) => {
      const button = document.getElementById(`cart_button-${item.id}`);
      if (button) {
        button.innerText = "Add to cart";
        button.style.backgroundColor = "#1677ff";
      }
    });

    cartItems = [];
    cartQuantity = 0; // Reset cart quantity counter
    updateCart(); // Update cart display
    updateLocalStorage(); // Update localStorage
    closeCartModal(); // Close the cart modal
    showMainButton(); // Hide the main button
  };

  // Handle click event on main button
  tg.MainButton.onClick(() => {
    const data = {
        cartItems: cartItems,   // Your cart items
        totalPrice: totalPrice  // Your total price
    };
    tg.sendData(JSON.stringify(data));
    clearCart(); // Clear cart after sending data
  });

  // Update main button visibility on page load
  showMainButton();
}