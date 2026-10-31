
document.addEventListener("DOMContentLoaded", function () {
    // MAP VARIABLES
    let map = null;
    let customerMarker = null;
    let pumpMarker = null;
    let customerCircle = null;
    let currentLatitude = null;
    let currentLongitude = null;
    let selectedStationType = "petrol";

    // ELEMENTS
    const locationText = document.getElementById("locationText");
    const nearestPump = document.getElementById("nearestPump");
    const pumpName = document.getElementById("pumpName");
    const pumpDistance = document.getElementById("pumpDistance");
    const navigateBtn = document.getElementById("navigateBtn");
    const petrolStationOption = document.getElementById("petrolStationOption");
    const cngStationOption = document.getElementById("cngStationOption");
    const findNearestStationBtn = document.getElementById("findNearestStationBtn");
    const stationSearchStatus = document.getElementById("stationSearchStatus");

    // SELECT PETROL OR CNG
    function selectStationType(type) {
        selectedStationType = type;

        if (petrolStationOption) {
            petrolStationOption.classList.toggle("selected", type === "petrol");
            petrolStationOption.setAttribute("aria-pressed", String(type === "petrol"));
        }

        if (cngStationOption) {
            cngStationOption.classList.toggle("selected", type === "cng");
            cngStationOption.setAttribute("aria-pressed", String(type === "cng"));
        }

        if (stationSearchStatus) {
            stationSearchStatus.textContent =
                type === "petrol" ? "Petrol Pump selected." : "CNG Station selected.";
        }

        if (nearestPump) nearestPump.style.display = "none";

        if (pumpMarker && map) {
            map.removeLayer(pumpMarker);
            pumpMarker = null;
        }
    }

    if (petrolStationOption) {
        petrolStationOption.addEventListener("click", function () {
            selectStationType("petrol");
        });
    }

    if (cngStationOption) {
        cngStationOption.addEventListener("click", function () {
            selectStationType("cng");
        });
    }

    // INITIALIZE WEBSITE MAP
    function initializeMap(latitude, longitude) {
        if (!window.L) {
            console.error("Leaflet library not loaded.");
            if (locationText) {
                locationText.textContent = "Map library failed to load.";
            }
            return;
        }

        if (map === null) {
            map = L.map("map", {
                zoomControl: true
            }).setView([latitude, longitude], 15);

            L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
                maxZoom: 19,
                attribution: "&copy; OpenStreetMap contributors"
            }).addTo(map);

            customerMarker = L.marker([latitude, longitude]).addTo(map);
            customerMarker.bindPopup("Your Location");

            customerCircle = L.circle([latitude, longitude], {
                radius: 40
            }).addTo(map);
        } else {
            map.setView([latitude, longitude], 15);

            if (customerMarker) {
                customerMarker.setLatLng([latitude, longitude]);
            }

            if (customerCircle) {
                customerCircle.setLatLng([latitude, longitude]);
            }
        }
    }

    // SAVE CUSTOMER LOCATION
    function updateCustomerLocation(latitude, longitude) {
        currentLatitude = latitude;
        currentLongitude = longitude;

        initializeMap(latitude, longitude);

        if (locationText) {
            locationText.textContent = "Location detected.";
        }

        // Station search does NOT start automatically.
    }

    // GPS ERROR
    function handleLocationError(error) {
        console.error("GPS Error:", error);

        if (!locationText) return;

        if (error.code === 1) {
            locationText.textContent = "Location permission denied.";
        } else if (error.code === 2) {
            locationText.textContent = "Unable to detect your location.";
        } else if (error.code === 3) {
            locationText.textContent = "Location request timed out.";
        } else {
            locationText.textContent = "Unable to get location.";
        }
    }

    // GET CUSTOMER GPS ONCE
    function getCustomerLocation() {
        if (!navigator.geolocation) {
            if (locationText) {
                locationText.textContent = "GPS is not supported by this browser.";
            }
            return;
        }

        if (locationText) {
            locationText.textContent = "Detecting your location...";
        }

        navigator.geolocation.getCurrentPosition(
            function (position) {
                updateCustomerLocation(
                    position.coords.latitude,
                    position.coords.longitude
                );
            },
            handleLocationError,
            {
                enableHighAccuracy: true,
                timeout: 15000,
                maximumAge: 0
            }
        );
    }

    // DISTANCE IN KILOMETRES
    function calculateDistance(lat1, lon1, lat2, lon2) {
        const earthRadius = 6371;
        const dLat = toRadians(lat2 - lat1);
        const dLon = toRadians(lon2 - lon1);

        const a =
            Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(toRadians(lat1)) *
            Math.cos(toRadians(lat2)) *
            Math.sin(dLon / 2) * Math.sin(dLon / 2);

        const c = 2 * Math.atan2(
            Math.sqrt(a),
            Math.sqrt(1 - a)
        );

        return earthRadius * c;
    }

    function toRadians(degrees) {
        return degrees * Math.PI / 180;
    }

    // FIND NEAREST PETROL PUMP OR CNG STATION
    async function findNearestPump(customerLat, customerLon) {
        try {
            if (stationSearchStatus) {
                stationSearchStatus.textContent = "Searching nearby stations...";
            }

            // Search within 8 km to reduce response size and waiting time.
            const query = `
                [out:json][timeout:12];
                (
                    node(around:8000,${customerLat},${customerLon})["amenity"="fuel"];
                    way(around:8000,${customerLat},${customerLon})["amenity"="fuel"];
                    relation(around:8000,${customerLat},${customerLon})["amenity"="fuel"];
                );
                out center tags;
            `;

            const response = await fetch(
                "https://overpass-api.de/api/interpreter",
                {
                    method: "POST",
                    headers: {
                        "Content-Type":
                            "application/x-www-form-urlencoded;charset=UTF-8"
                    },
                    body: "data=" + encodeURIComponent(query)
                }
            );

            if (!response.ok) {
                throw new Error("Station service is unavailable.");
            }

            const data = await response.json();

            const stations = (data.elements || [])
                .map(function (element) {
                    const tags = element.tags || {};
                    const latitude = element.lat ?? element.center?.lat;
                    const longitude = element.lon ?? element.center?.lon;

                    if (latitude === undefined || longitude === undefined) {
                        return null;
                    }

                    const hasCngTag = Object.keys(tags).some(function (key) {
                        return (
                            key.toLowerCase().includes("cng") &&
                            /^(yes|true|1|designated|customers)$/i.test(
                                String(tags[key])
                            )
                        );
                    });

                    const fuelTypes = String(tags.fuel || "")
                        .toLowerCase()
                        .split(/[;,]/)
                        .map(function (fuel) {
                            return fuel.trim();
                        });

                    const hasCngFuel =
                        hasCngTag || fuelTypes.includes("cng");

                    if (selectedStationType === "cng" && !hasCngFuel) {
                        return null;
                    }

                    return {
                        pump_name:
                            tags.name ||
                            tags.brand ||
                            (selectedStationType === "cng"
                                ? "CNG Station"
                                : "Petrol Pump"),
                        latitude: Number(latitude),
                        longitude: Number(longitude)
                    };
                })
                .filter(function (station) {
                    return (
                        station !== null &&
                        Number.isFinite(station.latitude) &&
                        Number.isFinite(station.longitude)
                    );
                });

            let nearest = null;
            let smallestDistance = Infinity;

            stations.forEach(function (station) {
                const distance = calculateDistance(
                    customerLat,
                    customerLon,
                    station.latitude,
                    station.longitude
                );

                if (
                    Number.isFinite(distance) &&
                    distance < smallestDistance
                ) {
                    smallestDistance = distance;
                    nearest = station;
                }
            });

            if (!nearest) {
                if (nearestPump) {
                    nearestPump.style.display = "none";
                }

                if (stationSearchStatus) {
                    stationSearchStatus.textContent =
                        "No matching station found within 8 km. Map data may be incomplete.";
                }
                return;
            }

            showNearestPump(nearest, smallestDistance);

            if (stationSearchStatus) {
                stationSearchStatus.textContent =
                    "Nearest station found. Opening Google Maps...";
            }

            const googleMapsUrl =
                "https://www.google.com/maps/dir/?api=1" +
                "&origin=" +
                encodeURIComponent(customerLat + "," + customerLon) +
                "&destination=" +
                encodeURIComponent(
                    nearest.latitude + "," + nearest.longitude
                ) +
                "&travelmode=driving";

            // Navigate in the current tab; no new browser tab is created.
            window.location.href = googleMapsUrl;

        } catch (error) {
            console.error("Nearest station error:", error);

            if (stationSearchStatus) {
                stationSearchStatus.textContent =
                    "Station search failed. Please try again.";
            }
        }
    }

    // DISPLAY NEAREST STATION
    function showNearestPump(pump, distance) {
        if (!nearestPump) return;

        nearestPump.style.display = "block";

        const stationIcon = selectedStationType === "cng" ? "🍃 " : "⛽ ";
        const stationName =
            pump.pump_name ||
            pump.station_name ||
            pump.name ||
            (selectedStationType === "cng" ? "CNG Station" : "Petrol Pump");

        if (pumpName) {
            pumpName.textContent = stationIcon + stationName;
        }

        if (pumpDistance) {
            pumpDistance.textContent = distance.toFixed(2) + " km Away";
        }

        if (map) {
            if (pumpMarker === null) {
                pumpMarker = L.marker([
                    pump.latitude,
                    pump.longitude
                ]).addTo(map);
            } else {
                pumpMarker.setLatLng([
                    pump.latitude,
                    pump.longitude
                ]);
            }

            pumpMarker.bindPopup(stationIcon + stationName);
            map.setView([pump.latitude, pump.longitude], 15);
            pumpMarker.openPopup();
        }

        // Navigation button also uses the saved customer location.
        if (navigateBtn) {
            navigateBtn.onclick = function () {
                if (
                    currentLatitude === null ||
                    currentLongitude === null
                ) {
                    alert("Your current location is not available.");
                    return;
                }

                const url =
                    "https://www.google.com/maps/dir/?api=1" +
                    "&origin=" +
                    encodeURIComponent(
                        currentLatitude + "," + currentLongitude
                    ) +
                    "&destination=" +
                    encodeURIComponent(
                        pump.latitude + "," + pump.longitude
                    ) +
                    "&travelmode=driving";

                window.location.href = url;
            };
        }
    }

    // SEARCH ONLY WHEN BUTTON IS CLICKED
    if (findNearestStationBtn) {
        findNearestStationBtn.addEventListener("click", function () {
            if (
                currentLatitude === null ||
                currentLongitude === null
            ) {
                if (stationSearchStatus) {
                    stationSearchStatus.textContent =
                        "Please allow GPS location access first.";
                }
                return;
            }

            findNearestPump(currentLatitude, currentLongitude);
        });
    }

    // START GPS ONCE
    getCustomerLocation();
});

// LIVE FUEL PRICE
async function updateFuelPrices() {
    try {
        const response = await fetch("/api/fuel-prices", {
            method: "GET",
            cache: "no-store"
        });

        if (!response.ok) {
            console.error("Fuel price API error");
            return;
        }

        const data = await response.json();

        if (!data.success) {
            console.error("Fuel price data unavailable");
            return;
        }

        const petrolPrice = document.getElementById("petrolPrice");

        if (petrolPrice && data.petrol !== undefined) {
            petrolPrice.textContent =
                "₹" + Number(data.petrol).toFixed(2) + "/L";
        }

        const dieselPrice = document.getElementById("dieselPrice");

        if (dieselPrice && data.diesel !== undefined) {
            dieselPrice.textContent =
                "₹" + Number(data.diesel).toFixed(2) + "/L";
        }

        const updated = document.getElementById("fuelPriceUpdated");

        if (updated && data.updated_at) {
            updated.textContent = "Updated: " + data.updated_at;
        }
    } catch (error) {
        console.error("Live fuel price error:", error);
    }
}

// Update prices when page loads, then every 5 minutes.
updateFuelPrices();
setInterval(updateFuelPrices, 5 * 60 * 1000);
