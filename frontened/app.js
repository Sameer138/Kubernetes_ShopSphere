const productsContainer =
    document.getElementById("products");
const ordersContainer =
    document.getElementById("orders");
const messageContainer =
    document.getElementById("message");
function showMessage(message, type) {
    messageContainer.textContent = message;
    messageContainer.className =
        `message ${type}`;
    messageContainer.style.display = "block";
    setTimeout(() => {
        messageContainer.style.display = "none";
    }, 4000);
}
async function loadProducts() {
    try {
        const response =
            await fetch("/api/products");
        if (!response.ok) {
            throw new Error(
                "Failed to fetch products"
            );
        }
        const products =
            await response.json();
        productsContainer.innerHTML = "";
        if (products.length === 0) {
            productsContainer.innerHTML =
                "<p>No products available.</p>";
            return;
        }
        products.forEach(product => {
            const card =
                document.createElement("div");
            card.className = "product-card";
            card.innerHTML = `
                <h3>${product.name}</h3>
                <p class="product-description">
                    ${product.description || ""}
                </p>
                <p class="price">
                    ₹${Number(product.price).toLocaleString("en-IN")}
                </p>
                <button
                    onclick="createOrder(${product.id})"
                >
                    Buy Now
                </button>
            `;
            productsContainer.appendChild(card);
        });
    } catch (error) {
        console.error(error);
        productsContainer.innerHTML =
            "<p>Unable to load products.</p>";
        showMessage(
            "Unable to connect to backend.",
            "error"
        );
    }
}
async function createOrder(productId) {
    try {
        const response =
            await fetch("/api/orders", {
                method: "POST",
                headers: {
                    "Content-Type":
                        "application/json"
                },
                body: JSON.stringify({
                    product_id: productId,
                    quantity: 1
                })
            });
        const data =
            await response.json();
        if (!response.ok) {
            throw new Error(
                data.detail ||
                "Failed to create order"
            );
        }
        showMessage(
            `Order #${data.id} created successfully!`,
            "success"
        );
        await loadOrders();
    } catch (error) {
        console.error(error);
        showMessage(
            error.message,
            "error"
        );
    }
}
async function loadOrders() {
    try {
        const response =
            await fetch("/api/orders");
        if (!response.ok) {
            throw new Error(
                "Failed to fetch orders"
            );
        }
        const orders =
            await response.json();
        ordersContainer.innerHTML = "";
        if (orders.length === 0) {
            ordersContainer.innerHTML = `
                <tr>
                    <td colspan="5">
                        No orders yet.
                    </td>
                </tr>
            `;
            return;
        }
        orders.forEach(order => {
            const row =
                document.createElement("tr");
            row.innerHTML = `
                <td>${order.id}</td>
                <td>${order.product_id}</td>
                <td>${order.quantity}</td>
                <td>
                    <span class="status">
                        ${order.status}
                    </span>
                </td>
                <td>
                    ${new Date(
                        order.created_at
                    ).toLocaleString()}
                </td>
            `;
            ordersContainer.appendChild(row);
        });
    } catch (error) {
        console.error(error);
        ordersContainer.innerHTML = `
            <tr>
                <td colspan="5">
                    Unable to load orders.
                </td>
            </tr>
        `;
    }
}
async function checkBackendHealth() {
    try {
        const response =
            await fetch("/health");
        const data =
            await response.json();
        console.log(
            "Backend health:",
            data
        );
    } catch (error) {
        console.error(
            "Backend health check failed:",
            error
        );
    }
}
async function initializeApplication() {
    console.log(
        "ShopSphere frontend starting..."
    );
    await checkBackendHealth();
    await loadProducts();
    await loadOrders();
}
initializeApplication();