
let quantity = 1;

const priceElement = document.getElementById("price");
const fuelPrice = priceElement
    ? parseFloat(priceElement.innerText) || 0
    : 0;

let deliveryCharge = 0;

let map = null;
let marker = null;

// ---------------- Price Calculation ----------------

function updatePrice() {
    const fuelCost = quantity * fuelPrice;
    const grandTotal = fuelCost + deliveryCharge;

    const fuelCostElement = document.getElementById("fuelCost");
    const deliveryChargeElement = document.getElementById("deliveryCharge");
    const grandTotalElement = document.getElementById("grandTotal");
    const quantityInput = document.getElementById("quantityInput");
    const priceInput = document.getElementById("priceInput");
    const quantityElement = document.getElementById("quantity");

    if (fuelCostElement) {
        fuelCostElement.innerText = fuelCost.toFixed(2);
    }

    if (deliveryChargeElement) {
        deliveryChargeElement.innerText = deliveryCharge.toFixed(2);
    }

    if (grandTotalElement) {
        grandTotalElement.innerText = grandTotal.toFixed(2);
    }

    if (quantityInput) {
        quantityInput.value = quantity;
    }

    if (priceInput) {
        priceInput.value = grandTotal.toFixed(2);
    }

    if (quantityElement) {
        quantityElement.innerText = quantity;
    }
}

// ---------------- Quantity Controls ----------------

function increaseQty() {
    quantity++;
    updatePrice();
}

function decreaseQty() {
    if (quantity > 1) {
        quantity--;
        updatePrice();
    }
}

// ---------------- Delivery Quote ----------------

async function updateDeliveryQuote(latitude, longitude) {
    try {
        const fuelInput = document.querySelector('input[name="fuel"]');

        const response = await fetch(
            "/api/delivery_quote?" +
            new URLSearchParams({
                latitude: latitude,
                longitude: longitude,
                fuel: fuelInput ? fuelInput.value : "",
                quantity: quantity
            }),
            {
                method: "GET",
                credentials: "same-origin",
                cache: "no-store"
            }
        );

        if (!response.ok) {
            console.error("Delivery quote request failed:", response.status);
            return;
        }

        const data = await response.json();

        if (data.success !== true) {
            console.error("Delivery quote error:", data);
            return;
        }

        deliveryCharge = Number(data.delivery_charge) || 0;
        updatePrice();

    } catch (error) {
        console.error("Delivery quote error:", error);
    }
}

// ---------------- Form Validation ----------------

function validateOrder() {
    const phoneElement = document.getElementById("phone");
    const addressElement = document.getElementById("address");

    if (!phoneElement || !addressElement) {
        console.error("Phone or address field not found.");
        alert("Form error. Please refresh the page.");
        return false;
    }

    const phone = phoneElement.value.trim();
    const address = addressElement.value.trim();

    if (!/^[0-9]{10}$/.test(phone)) {
        alert("Enter a valid 10-digit mobile number.");
        phoneElement.focus();
        return false;
    }

    if (address === "") {
        alert("Please enter your delivery address.");
        addressElement.focus();
        return false;
    }

    const quantityInput = document.getElementById("quantityInput");

    if (!quantityInput || Number(quantityInput.value) <= 0) {
        alert("Please select a valid fuel quantity.");
        return false;
    }

    console.log("Order form validation passed.");
    return true;
}

// ---------------- Current Location ----------------

function getLocation() {
    if (!navigator.geolocation) {
        alert("Geolocation is not supported by your browser.");
        return;
    }

    navigator.geolocation.getCurrentPosition(
        showPosition,
        showError,
        {
            enableHighAccuracy: true,
            timeout: 15000,
            maximumAge: 0
        }
    );
}

// ---------------- Show Current Location ----------------

function showPosition(position) {
    const lat = position.coords.latitude;
    const lng = position.coords.longitude;

    const addressElement = document.getElementById("address");
    const latitudeElement = document.getElementById("latitude");
    const longitudeElement = document.getElementById("longitude");

    if (addressElement) {
        addressElement.value =
            "Latitude: " + lat + "\nLongitude: " + lng;
    }

    if (latitudeElement) {
        latitudeElement.value = lat;
    }

    if (longitudeElement) {
        longitudeElement.value = lng;
    }

    updateDeliveryQuote(lat, lng);

    if (typeof L === "undefined" || !document.getElementById("map")) {
        return;
    }

    if (map) {
        map.remove();
        map = null;
        marker = null;
    }

    map = L.map("map").setView([lat, lng], 16);

    L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
            attribution: "&copy; OpenStreetMap contributors"
        }
    ).addTo(map);

    marker = L.marker([lat, lng], {
        draggable: true
    }).addTo(map);

    marker.on("dragend", function () {
        const position = marker.getLatLng();

        if (addressElement) {
            addressElement.value =
                "Latitude: " + position.lat +
                "\nLongitude: " + position.lng;
        }

        if (latitudeElement) {
            latitudeElement.value = position.lat;
        }

        if (longitudeElement) {
            longitudeElement.value = position.lng;
        }

        updateDeliveryQuote(position.lat, position.lng);
    });
}

// ---------------- Location Error ----------------

function showError(error) {
    let message = "Unable to get your location.";

    if (error && error.code === 1) {
        message = "Please allow location permission in your browser.";
    } else if (error && error.code === 2) {
        message = "Your current location is unavailable.";
    } else if (error && error.code === 3) {
        message = "Location request timed out. Please try again.";
    }

    alert(message);
}

// ---------------- Initial Setup ----------------

document.addEventListener("DOMContentLoaded", function () {
    updatePrice();

    const orderForm = document.querySelector('form[action*="place_order"]');

    if (orderForm) {
        orderForm.addEventListener("submit", function (event) {
            console.log("Place Order clicked. Submitting form...");

            if (!validateOrder()) {
                event.preventDefault();
            }
        });
    }
});
