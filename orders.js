document.addEventListener(
    "DOMContentLoaded",
    function () {

        // =====================================================
        // STATE
        // =====================================================

        let refreshing = false;

        const trackingTimers = {};

        const maps = {};

        const pumpMarkers = {};

        const customerMarkers = {};

        const routeLines = {};


        // =====================================================
        // CUSTOMER ORDERS LIVE API
        // =====================================================

        async function refreshOrders() {

            if (refreshing) {
                return;
            }

            refreshing = true;

            try {

                const response =
                    await fetch(
                        "/api/my_orders?t=" +
                        Date.now(),
                        {
                            method: "GET",

                            credentials:
                                "same-origin",

                            cache: "no-store",

                            headers: {
                                "Accept":
                                    "application/json",

                                "Cache-Control":
                                    "no-cache",

                                "Pragma":
                                    "no-cache"
                            }
                        }
                    );


                if (!response.ok) {
                    return;
                }


                const data =
                    await response.json();


                if (
                    !data ||
                    data.success !== true ||
                    !Array.isArray(data.orders)
                ) {

                    return;

                }


                // =================================================
                // UPDATE EXISTING ORDERS
                // =================================================

                data.orders.forEach(
                    function (order) {

                        updateOrderCard(
                            order
                        );

                    }
                );


                // =================================================
                // REMOVE CLEARED ORDERS
                // =================================================

                const serverIds =
                    new Set(
                        data.orders.map(
                            function (order) {

                                return String(
                                    order.id
                                );

                            }
                        )
                    );


                document
                    .querySelectorAll(
                        ".order-card[data-order-id]"
                    )
                    .forEach(
                        function (card) {

                            const id =
                                String(
                                    card.dataset.orderId
                                );


                            if (
                                !serverIds.has(id)
                            ) {

                                stopTracking(id);

                                card.remove();

                            }

                        }
                    );


                showEmptyMessageIfNeeded();


            } catch (error) {

                console.error(
                    "Live orders error:",
                    error
                );

            } finally {

                refreshing = false;

            }

        }


        // =====================================================
        // UPDATE ORDER CARD
        // =====================================================

        function updateOrderCard(order) {

            const card =
                document.querySelector(
                    '.order-card[data-order-id="' +
                    order.id +
                    '"]'
                );


            if (!card) {
                return;
            }


            const statusElement =
                card.querySelector(
                    "[data-status]"
                );


            const orderStatusElement =
                card.querySelector(
                    ".order-status"
                );


            const paymentStatusElement =
                card.querySelector(
                    ".payment-status"
                );


            // =================================================
            // OTP
            // =================================================

            updateDeliveryOtp(
                card,
                order
            );


            // =================================================
            // CANCELLED
            // =================================================

            if (
                Number(order.cancelled) === 1
            ) {

                setStatus(
                    statusElement,
                    "Cancelled",
                    "status rejected"
                );


                if (orderStatusElement) {

                    orderStatusElement.textContent =
                        order.status ||
                        "Cancelled";

                }


                stopTracking(
                    order.id
                );


                updateActions(
                    card,
                    order
                );


                return;

            }


            // =================================================
            // COMPLETED
            // =================================================

            if (
                order.delivery_status ===
                "Completed"
            ) {

                setStatus(
                    statusElement,
                    "Completed",
                    "status completed"
                );


                if (orderStatusElement) {

                    orderStatusElement.textContent =
                        "Completed";

                }


                stopTracking(
                    order.id
                );


                updateActions(
                    card,
                    order
                );


                return;

            }


            // =================================================
            // ON THE WAY
            // =================================================

            if (
                order.delivery_status ===
                "On The Way"
            ) {

                setStatus(
                    statusElement,
                    "On The Way",
                    "status way"
                );


                if (orderStatusElement) {

                    orderStatusElement.textContent =
                        "On The Way";

                }


                updateActions(
                    card,
                    order
                );


                if (
                    card.dataset.trackingOpen ===
                    "true"
                ) {

                    startTracking(
                        order.id
                    );

                }


                return;

            }


            // =================================================
            // ACCEPTED
            // =================================================

            if (
                Number(order.accepted) === 1
            ) {

                setStatus(
                    statusElement,
                    "Accepted",
                    "status accepted"
                );


                if (orderStatusElement) {

                    orderStatusElement.textContent =
                        order.status ||
                        "Accepted";

                }


                updateActions(
                    card,
                    order
                );


                return;

            }


            // =================================================
            // PENDING
            // =================================================

            setStatus(
                statusElement,
                "Pending Approval",
                "status pending"
            );


            if (orderStatusElement) {

                orderStatusElement.textContent =
                    order.status ||
                    "Pending Approval";

            }


            updateActions(
                card,
                order
            );

        }


        // =====================================================
        // DELIVERY OTP UPDATE
        // =====================================================

        function updateDeliveryOtp(
            card,
            order
        ) {

            let otpBox =
                card.querySelector(
                    "[data-otp-box]"
                );


            let otpElement =
                card.querySelector(
                    "[data-delivery-otp]"
                );


            // =================================================
            // SHOW OTP
            // =================================================

            if (
                Number(order.accepted) === 1 &&
                Number(order.cancelled) !== 1 &&
                order.delivery_status !==
                    "Completed" &&
                order.delivery_otp
            ) {

                // ---------------------------------------------
                // CREATE OTP BOX IF MISSING
                // ---------------------------------------------

                if (!otpBox) {

                    otpBox =
                        document.createElement(
                            "div"
                        );


                    otpBox.className =
                        "delivery-otp-box";


                    otpBox.setAttribute(
                        "data-otp-box",
                        ""
                    );


                    otpBox.innerHTML =

                        '<div class="delivery-otp-title">' +
                            '🔐 Delivery OTP' +
                        '</div>' +

                        '<div ' +
                            'class="delivery-otp-number" ' +
                            'data-delivery-otp' +
                        '></div>' +

                        '<div class="delivery-otp-note">' +
                            'Delivery complete karne ke liye ' +
                            'ye OTP delivery person ko batayein.' +
                        '</div>';


                    const payment =
                        card.querySelector(
                            ".payment-status"
                        );


                    if (payment) {

                        payment.insertAdjacentElement(
                            "afterend",
                            otpBox
                        );

                    } else {

                        const actions =
                            card.querySelector(
                                ".actions"
                            );


                        if (actions) {

                            actions.parentNode.insertBefore(
                                otpBox,
                                actions
                            );

                        }

                    }


                    otpElement =
                        otpBox.querySelector(
                            "[data-delivery-otp]"
                        );

                }


                // ---------------------------------------------
                // UPDATE OTP
                // ---------------------------------------------

                if (otpElement) {

                    otpElement.textContent =
                        String(
                            order.delivery_otp
                        );

                }


                otpBox.style.display =
                    "block";

            }

            // =================================================
            // HIDE OTP
            // =================================================

            else {

                if (otpBox) {

                    otpBox.style.display =
                        "none";

                }

            }

        }


        // =====================================================
        // STATUS
        // =====================================================

        function setStatus(
            element,
            text,
            className
        ) {

            if (!element) {
                return;
            }


            element.textContent =
                text;


            element.className =
                className;

        }


        // =====================================================
        // UPDATE ACTION BUTTONS
        // =====================================================

        function updateActions(
            card,
            order
        ) {

            const actions =
                card.querySelector(
                    ".actions"
                );


            if (!actions) {
                return;
            }


            // =================================================
            // PAYMENT STATUS
            // =================================================

            const paymentStatus =
                card.querySelector(
                    ".payment-status"
                );


            if (paymentStatus) {

                if (
                    order.payment_status ===
                    "Paid"
                ) {

                    paymentStatus.innerHTML =
                        '<span class="paid">' +
                        'Paid' +
                        '</span>';

                } else {

                    paymentStatus.innerHTML =
                        '<span class="unpaid">' +
                        (
                            order.payment_status ||
                            "Pending"
                        ) +
                        '</span>';

                }

            }


            // =================================================
            // EXISTING BUTTONS
            // =================================================

            const callButton =
                actions.querySelector(
                    ".call-btn"
                );


            const trackButton =
                actions.querySelector(
                    ".track-button"
                );


            const payButton =
                actions.querySelector(
                    ".pay-btn"
                );


            const cancelForm =
                actions.querySelector(
                    "form"
                );


            // =================================================
            // CANCELLED / COMPLETED
            // =================================================

            if (
                Number(order.cancelled) === 1 ||
                order.delivery_status ===
                    "Completed"
            ) {

                if (trackButton) {

                    trackButton.style.display =
                        "none";

                }


                if (payButton) {

                    payButton.style.display =
                        "none";

                }


                if (cancelForm) {

                    cancelForm.style.display =
                        "none";

                }


                return;

            }


            // =================================================
            // ACCEPTED
            // =================================================

            if (
                Number(order.accepted) === 1
            ) {

                if (cancelForm) {

                    cancelForm.style.display =
                        "none";

                }


                // ---------------------------------------------
                // LIVE TRACKING
                // ---------------------------------------------

                let finalTrackButton =
                    trackButton;


                if (!finalTrackButton) {

                    finalTrackButton =
                        document.createElement(
                            "button"
                        );


                    finalTrackButton.type =
                        "button";


                    finalTrackButton.className =
                        "btn track-btn track-button";


                    finalTrackButton.textContent =
                        "📍 Live Tracking";


                    actions.appendChild(
                        finalTrackButton
                    );

                }


                finalTrackButton.style.display =
                    "block";


                bindTrackButton(
                    finalTrackButton
                );


                // ---------------------------------------------
                // PAYMENT
                // ---------------------------------------------

                if (
                    order.payment_status !==
                    "Paid"
                ) {

                    let finalPayButton =
                        payButton;


                    if (!finalPayButton) {

                        finalPayButton =
                            document.createElement(
                                "a"
                            );


                        finalPayButton.className =
                            "btn pay-btn";


                        finalPayButton.textContent =
                            "💳 Pay Now";


                        actions.appendChild(
                            finalPayButton
                        );

                    }


                    finalPayButton.href =
                        "/payment/" +
                        encodeURIComponent(
                            order.id
                        );


                    finalPayButton.style.display =
                        "block";

                }

                else {

                    if (payButton) {

                        payButton.remove();

                    }

                }


                return;

            }


            // =================================================
            // PENDING
            // =================================================

            if (trackButton) {

                trackButton.style.display =
                    "none";

            }


            if (payButton) {

                payButton.style.display =
                    "none";

            }


            if (cancelForm) {

                cancelForm.style.display =
                    "";

            }

        }


        // =====================================================
        // TRACK BUTTON BINDING
        // =====================================================

        function bindTrackButton(
            button
        ) {

            if (
                button.dataset.bound ===
                "true"
            ) {

                return;

            }


            button.dataset.bound =
                "true";


            button.addEventListener(
                "click",
                function () {

                    const card =
                        button.closest(
                            ".order-card"
                        );


                    if (!card) {
                        return;
                    }


                    toggleTracking(
                        card
                    );

                }
            );

        }


        // =====================================================
        // EXISTING TRACK BUTTONS
        // =====================================================

        document
            .querySelectorAll(
                ".track-button"
            )
            .forEach(
                function (button) {

                    bindTrackButton(
                        button
                    );

                }
            );


        // =====================================================
        // TOGGLE TRACKING
        // =====================================================

        function toggleTracking(
            card
        ) {

            const orderId =
                card.dataset.orderId;


            const section =
                card.querySelector(
                    ".tracking-section"
                );


            if (!section) {
                return;
            }


            if (
                section.style.display ===
                "block"
            ) {

                section.style.display =
                    "none";


                card.dataset.trackingOpen =
                    "false";


                stopTracking(
                    orderId
                );


                return;

            }


            section.style.display =
                "block";


            card.dataset.trackingOpen =
                "true";


            loadTrackingLocation(
                orderId
            );


            startTracking(
                orderId
            );

        }


        // =====================================================
        // START TRACKING
        // =====================================================

        function startTracking(
            orderId
        ) {

            if (
                trackingTimers[orderId]
            ) {

                return;

            }


            loadTrackingLocation(
                orderId
            );


            trackingTimers[orderId] =
                setInterval(
                    function () {

                        loadTrackingLocation(
                            orderId
                        );

                    },
                    3000
                );

        }


        // =====================================================
        // STOP TRACKING
        // =====================================================

        function stopTracking(
            orderId
        ) {

            if (
                trackingTimers[orderId]
            ) {

                clearInterval(
                    trackingTimers[orderId]
                );


                delete trackingTimers[
                    orderId
                ];

            }

        }


        // =====================================================
        // LOAD TRACKING LOCATION
        // =====================================================

        async function loadTrackingLocation(
            orderId
        ) {

            try {

                const response =
                    await fetch(
                        "/delivery_location/" +
                        encodeURIComponent(
                            orderId
                        ) +
                        "?t=" +
                        Date.now(),
                        {
                            method: "GET",

                            credentials:
                                "same-origin",

                            cache: "no-store",

                            headers: {
                                "Accept":
                                    "application/json"
                            }
                        }
                    );


                if (!response.ok) {
                    return;
                }


                const data =
                    await response.json();


                if (
                    !data ||
                    data.success !== true
                ) {

                    return;

                }


                drawTrackingMap(
                    orderId,
                    data
                );


            } catch (error) {

                console.error(
                    "Tracking error:",
                    error
                );

            }

        }


        // =====================================================
        // DRAW TRACKING MAP
        // =====================================================

        function drawTrackingMap(
            orderId,
            data
        ) {

            const customer =
                data.customer;


            const pump =
                data.pump;


            if (
                !customer ||
                customer.lat === null ||
                customer.lon === null
            ) {

                updateTrackingInfo(
                    orderId,
                    "Customer location is not available."
                );


                return;

            }


            if (
                !pump ||
                pump.lat === null ||
                pump.lon === null
            ) {

                updateTrackingInfo(
                    orderId,
                    "Waiting for delivery location..."
                );


                return;

            }


            const customerLat =
                Number(
                    customer.lat
                );


            const customerLon =
                Number(
                    customer.lon
                );


            const pumpLat =
                Number(
                    pump.lat
                );


            const pumpLon =
                Number(
                    pump.lon
                );


            if (
                !Number.isFinite(
                    customerLat
                ) ||
                !Number.isFinite(
                    customerLon
                ) ||
                !Number.isFinite(
                    pumpLat
                ) ||
                !Number.isFinite(
                    pumpLon
                )
            ) {

                return;

            }


            const mapElement =
                document.getElementById(
                    "map-" +
                    orderId
                );


            if (!mapElement) {
                return;
            }


            // =================================================
            // CREATE MAP
            // =================================================

            if (!maps[orderId]) {

                maps[orderId] =
                    L.map(
                        mapElement
                    ).setView(
                        [
                            pumpLat,
                            pumpLon
                        ],
                        14
                    );


                L.tileLayer(
                    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                    {
                        maxZoom: 19,

                        attribution:
                            "&copy; OpenStreetMap contributors"
                    }
                ).addTo(
                    maps[orderId]
                );


                customerMarkers[
                    orderId
                ] =
                    L.marker(
                        [
                            customerLat,
                            customerLon
                        ]
                    )
                    .addTo(
                        maps[orderId]
                    )
                    .bindPopup(
                        "Delivery Destination"
                    );


                pumpMarkers[
                    orderId
                ] =
                    L.marker(
                        [
                            pumpLat,
                            pumpLon
                        ]
                    )
                    .addTo(
                        maps[orderId]
                    )
                    .bindPopup(
                        "Delivery Vehicle"
                    );


                routeLines[
                    orderId
                ] =
                    L.polyline(
                        [
                            [
                                pumpLat,
                                pumpLon
                            ],

                            [
                                customerLat,
                                customerLon
                            ]
                        ]
                    )
                    .addTo(
                        maps[orderId]
                    );


                maps[
                    orderId
                ].fitBounds(
                    [
                        [
                            pumpLat,
                            pumpLon
                        ],

                        [
                            customerLat,
                            customerLon
                        ]
                    ],
                    {
                        padding:
                            [
                                30,
                                30
                            ]
                    }
                );


            }

            // =================================================
            // UPDATE MAP
            // =================================================

            else {

                pumpMarkers[
                    orderId
                ].setLatLng(
                    [
                        pumpLat,
                        pumpLon
                    ]
                );


                customerMarkers[
                    orderId
                ].setLatLng(
                    [
                        customerLat,
                        customerLon
                    ]
                );


                routeLines[
                    orderId
                ].setLatLngs(
                    [
                        [
                            pumpLat,
                            pumpLon
                        ],

                        [
                            customerLat,
                            customerLon
                        ]
                    ]
                );

            }


            updateTrackingInfo(
                orderId,
                "Delivery Status: " +
                (
                    data.delivery_status ||
                    data.status ||
                    "Unknown"
                )
            );

        }


        // =====================================================
        // TRACKING INFO
        // =====================================================

        function updateTrackingInfo(
            orderId,
            message
        ) {

            const element =
                document.getElementById(
                    "tracking-info-" +
                    orderId
                );


            if (element) {

                element.textContent =
                    message;

            }

        }


        // =====================================================
        // EMPTY MESSAGE
        // =====================================================

        function showEmptyMessageIfNeeded() {

            const cards =
                document.querySelectorAll(
                    ".order-card"
                );


            const container =
                document.querySelector(
                    ".container"
                );


            if (!container) {
                return;
            }


            let empty =
                container.querySelector(
                    ".live-empty-message"
                );


            if (
                cards.length === 0
            ) {

                if (!empty) {

                    empty =
                        document.createElement(
                            "div"
                        );


                    empty.className =
                        "empty live-empty-message";


                    empty.innerHTML =

                        '<div class="empty-icon">' +
                            '📦' +
                        '</div>' +

                        '<h2>' +
                            'My Orders' +
                        '</h2>' +

                        '<p style="margin-top:10px;">' +
                            'No orders found.' +
                        '</p>';


                    container.appendChild(
                        empty
                    );

                }

            }

            else {

                if (empty) {

                    empty.remove();

                }

            }

        }


        // =====================================================
        // CLEAR ORDERS
        // =====================================================

        const clearButton =
            document.getElementById(
                "clearOrdersButton"
            );


        if (clearButton) {

            clearButton.addEventListener(
                "click",
                async function () {

                    const confirmed =
                        confirm(
                            "Are you sure you want to clear all your orders?"
                        );


                    if (!confirmed) {
                        return;
                    }


                    clearButton.disabled =
                        true;


                    clearButton.textContent =
                        "Clearing...";


                    try {

                        const response =
                            await fetch(
                                "/customer_clear_orders",
                                {
                                    method: "POST",

                                    credentials:
                                        "same-origin",

                                    cache: "no-store",

                                    headers: {
                                        "Accept":
                                            "application/json",

                                        "Content-Type":
                                            "application/json"
                                    },

                                    body:
                                        JSON.stringify({})
                                }
                            );


                        const data =
                            await response.json();


                        if (
                            response.ok &&
                            data.success === true
                        ) {

                            Object.keys(
                                trackingTimers
                            ).forEach(
                                function (
                                    orderId
                                ) {

                                    stopTracking(
                                        orderId
                                    );

                                }
                            );


                            Object.keys(
                                maps
                            ).forEach(
                                function (
                                    orderId
                                ) {

                                    if (
                                        maps[orderId]
                                    ) {

                                        maps[
                                            orderId
                                        ].remove();

                                    }

                                    delete maps[
                                        orderId
                                    ];

                                    delete pumpMarkers[
                                        orderId
                                    ];

                                    delete customerMarkers[
                                        orderId
                                    ];

                                    delete routeLines[
                                        orderId
                                    ];

                                }
                            );


                            document
                                .querySelectorAll(
                                    ".order-card"
                                )
                                .forEach(
                                    function (
                                        card
                                    ) {

                                        card.remove();

                                    }
                                );


                            showEmptyMessageIfNeeded();


                        }

                        else {

                            alert(
                                data.message ||
                                "Unable to clear orders."
                            );

                        }


                    }

                    catch (error) {

                        console.error(
                            "Clear orders error:",
                            error
                        );


                        alert(
                            "Unable to clear orders."
                        );

                    }

                    finally {

                        clearButton.disabled =
                            false;


                        clearButton.textContent =
                            "🗑️ Clear Orders";

                    }

                }
            );

        }


        // =====================================================
        // INITIAL LOAD
        // =====================================================

        refreshOrders();


        // =====================================================
        // LIVE UPDATE EVERY 2 SECONDS
        // =====================================================

        setInterval(
            refreshOrders,
            2000
        );


        // =====================================================
        // WHEN USER RETURNS TO PAGE
        // =====================================================

        document.addEventListener(
            "visibilitychange",
            function () {

                if (
                    document.visibilityState ===
                    "visible"
                ) {

                    refreshOrders();

                }

            }
        );


        // =====================================================
        // CLEANUP
        // =====================================================

        window.addEventListener(
            "beforeunload",
            function () {

                Object.keys(
                    trackingTimers
                ).forEach(
                    function (
                        orderId
                    ) {

                        stopTracking(
                            orderId
                        );

                    }
                );

            }
        );

    }
);