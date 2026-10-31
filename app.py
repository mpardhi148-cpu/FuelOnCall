import os
import secrets
import json
import urllib.request
import urllib.parse
import urllib.error 

from datetime import datetime, timedelta, timezone
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    send_from_directory,
    jsonify,
    Response
)

from Database.db import get_connection

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from jinja2 import (
    ChoiceLoader,
    FileSystemLoader
)


# =========================================================
# APP CONFIGURATION
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

CUSTOMER_TEMPLATES = os.path.join(
    BASE_DIR,
    "templates"
)

PETROL_TEMPLATES = os.path.join(
    BASE_DIR,
    "Fproject",
    "petrol_templates"
)

CUSTOMER_STATIC = os.path.join(
    BASE_DIR,
    "static"
)

PETROL_STATIC = os.path.join(
    BASE_DIR,
    "Fproject",
    "static"
)


app = Flask(
    __name__,
    static_folder=None
)


app.secret_key = "fueloncall_secret_key"

app.config["SESSION_COOKIE_NAME"] = "fueloncall_session"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False

app.config["PERMANENT_SESSION_LIFETIME"] = 60 * 60 * 24 * 365

# ============================================================
# LANGUAGE SYSTEM
# ============================================================

SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
    "gu": "Gujarati",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi"
}


LANGUAGE_NAMES = SUPPORTED_LANGUAGES


TRANSLATIONS = {

    "en": {
        "app_name": "FuelOnCall",
        "home": "Home",
        "orders": "Orders",
        "profile": "Profile",
        "settings": "Settings",
        "need_help": "Need Help",
        "logout": "Logout",
        "save": "Save",
        "language": "Language",
        "back": "Back",
        "back_home": "Back to Home",
        "back_profile": "Back to Profile",
        "back_settings": "Back to Settings",
        "back_dashboard": "Back to Dashboard",

        "welcome": "Welcome",
        "choose_fuel": "Choose Fuel",
        "petrol": "Petrol",
        "diesel": "Diesel",
        "place_order": "Place Order",
        "quantity": "Quantity",
        "amount": "Amount",
        "address": "Address",
        "payment": "Payment",
        "payment_method": "Payment Method",
        "cash_on_delivery": "Cash on Delivery",
        "online_payment": "Online Payment",
        "cancel_order": "Cancel Order",

        "pending": "Pending",
        "accepted": "Accepted",
        "rejected": "Rejected",
        "completed": "Completed",
        "delivery": "Delivery",
        "delivery_status": "Delivery Status",
        "current_deliveries": "Current Deliveries",
        "fuel_requests": "Fuel Requests",

        "fast_delivery": "Fast Delivery",
        "fair_price": "Fair Price",
        "safe_service": "Safe Service",
        "live_tracking": "Live Tracking",

        "mobile": "Mobile",
        "email": "Email",
        "name": "Name",
        "total_orders": "Total Orders",

        "call_customer": "Call Customer",
        "call_pump": "Call Petrol Pump",

        "dashboard": "Dashboard",
        "customers": "Customers",
        "reports": "Reports",
        "earnings": "Earnings",
        "daily_orders": "Daily Orders",
        "my_deliveries": "My Deliveries",

        "fuel_price": "Fuel Price",
        "delivery_charge": "Delivery Charge",
        "total": "Total",

        "how_to_use": "How to Use",
        "order_fuel": "Order Fuel",
        "track_delivery": "Track Delivery",
        "contact_support": "Contact Support",

        "pump_profile": "Petrol Pump Profile",
        "pump_settings": "Petrol Pump Settings",
        "new_request": "New Fuel Request",
        "accept_order": "Accept Order",
        "reject_order": "Reject Order",
        "start_delivery": "Start Delivery",
        "update_status": "Update Status",

        "something_wrong": "Something went wrong",
        "try_again": "Please try again",

        "no_orders": "No Orders Found",
        "no_requests": "No Fuel Requests Found"
    },


    "hi": {
        "app_name": "फ्यूलऑनकॉल",
        "home": "होम",
        "orders": "ऑर्डर",
        "profile": "प्रोफाइल",
        "settings": "सेटिंग्स",
        "need_help": "मदद चाहिए",
        "logout": "लॉगआउट",
        "save": "सेव करें",
        "language": "भाषा",
        "back": "वापस",
        "back_home": "होम पर वापस जाएँ",
        "back_profile": "प्रोफाइल पर वापस जाएँ",
        "back_settings": "सेटिंग्स पर वापस जाएँ",
        "back_dashboard": "डैशबोर्ड पर वापस जाएँ",

        "welcome": "स्वागत है",
        "choose_fuel": "ईंधन चुनें",
        "petrol": "पेट्रोल",
        "diesel": "डीजल",
        "place_order": "ऑर्डर करें",
        "quantity": "मात्रा",
        "amount": "राशि",
        "address": "पता",
        "payment": "भुगतान",
        "payment_method": "भुगतान का तरीका",
        "cash_on_delivery": "कैश ऑन डिलीवरी",
        "online_payment": "ऑनलाइन भुगतान",
        "cancel_order": "ऑर्डर रद्द करें",

        "pending": "लंबित",
        "accepted": "स्वीकृत",
        "rejected": "अस्वीकृत",
        "completed": "पूरा हुआ",
        "delivery": "डिलीवरी",
        "delivery_status": "डिलीवरी स्थिति",
        "current_deliveries": "वर्तमान डिलीवरी",
        "fuel_requests": "ईंधन अनुरोध",

        "fast_delivery": "तेज़ डिलीवरी",
        "fair_price": "उचित कीमत",
        "safe_service": "सुरक्षित सेवा",
        "live_tracking": "लाइव ट्रैकिंग",

        "mobile": "मोबाइल",
        "email": "ईमेल",
        "name": "नाम",
        "total_orders": "कुल ऑर्डर",

        "call_customer": "ग्राहक को कॉल करें",
        "call_pump": "पेट्रोल पंप को कॉल करें",

        "dashboard": "डैशबोर्ड",
        "customers": "ग्राहक",
        "reports": "रिपोर्ट",
        "earnings": "कमाई",
        "daily_orders": "दैनिक ऑर्डर",
        "my_deliveries": "मेरी डिलीवरी",

        "fuel_price": "ईंधन की कीमत",
        "delivery_charge": "डिलीवरी शुल्क",
        "total": "कुल",

        "how_to_use": "कैसे उपयोग करें",
        "order_fuel": "ईंधन ऑर्डर करें",
        "track_delivery": "डिलीवरी ट्रैक करें",
        "contact_support": "सहायता से संपर्क करें",

        "pump_profile": "पेट्रोल पंप प्रोफाइल",
        "pump_settings": "पेट्रोल पंप सेटिंग्स",
        "new_request": "नया ईंधन अनुरोध",
        "accept_order": "ऑर्डर स्वीकार करें",
        "reject_order": "ऑर्डर अस्वीकार करें",
        "start_delivery": "डिलीवरी शुरू करें",
        "update_status": "स्थिति अपडेट करें",

        "something_wrong": "कुछ गलत हो गया",
        "try_again": "कृपया फिर कोशिश करें",

        "no_orders": "कोई ऑर्डर नहीं मिला",
        "no_requests": "कोई ईंधन अनुरोध नहीं मिला"
    },


    "mr": {
        "app_name": "फ्यूलऑनकॉल",
        "home": "मुख्यपृष्ठ",
        "orders": "ऑर्डर्स",
        "profile": "प्रोफाइल",
        "settings": "सेटिंग्ज",
        "need_help": "मदत हवी आहे",
        "logout": "लॉगआउट",
        "save": "जतन करा",
        "language": "भाषा",
        "back": "मागे",
        "back_home": "मुख्यपृष्ठावर जा",
        "back_profile": "प्रोफाइलवर जा",
        "back_settings": "सेटिंग्जवर जा",
        "back_dashboard": "डॅशबोर्डवर जा",

        "welcome": "स्वागत आहे",
        "choose_fuel": "इंधन निवडा",
        "petrol": "पेट्रोल",
        "diesel": "डिझेल",
        "place_order": "ऑर्डर करा",
        "quantity": "प्रमाण",
        "amount": "रक्कम",
        "address": "पत्ता",
        "payment": "पेमेंट",
        "payment_method": "पेमेंट पद्धत",
        "cash_on_delivery": "कॅश ऑन डिलिव्हरी",
        "online_payment": "ऑनलाइन पेमेंट",
        "cancel_order": "ऑर्डर रद्द करा",

        "pending": "प्रलंबित",
        "accepted": "स्वीकृत",
        "rejected": "नाकारले",
        "completed": "पूर्ण",
        "delivery": "डिलिव्हरी",
        "delivery_status": "डिलिव्हरी स्थिती",
        "current_deliveries": "सध्याच्या डिलिव्हरी",
        "fuel_requests": "इंधन विनंत्या",

        "fast_delivery": "जलद डिलिव्हरी",
        "fair_price": "योग्य किंमत",
        "safe_service": "सुरक्षित सेवा",
        "live_tracking": "लाइव्ह ट्रॅकिंग",

        "mobile": "मोबाइल",
        "email": "ईमेल",
        "name": "नाव",
        "total_orders": "एकूण ऑर्डर्स",

        "call_customer": "ग्राहकाला कॉल करा",
        "call_pump": "पेट्रोल पंपाला कॉल करा",

        "dashboard": "डॅशबोर्ड",
        "customers": "ग्राहक",
        "reports": "अहवाल",
        "earnings": "कमाई",
        "daily_orders": "दैनिक ऑर्डर्स",
        "my_deliveries": "माझ्या डिलिव्हरी",

        "fuel_price": "इंधनाची किंमत",
        "delivery_charge": "डिलिव्हरी शुल्क",
        "total": "एकूण",

        "how_to_use": "कसे वापरावे",
        "order_fuel": "इंधन ऑर्डर करा",
        "track_delivery": "डिलिव्हरी ट्रॅक करा",
        "contact_support": "सहाय्याशी संपर्क करा",

        "pump_profile": "पेट्रोल पंप प्रोफाइल",
        "pump_settings": "पेट्रोल पंप सेटिंग्ज",
        "new_request": "नवीन इंधन विनंती",
        "accept_order": "ऑर्डर स्वीकारा",
        "reject_order": "ऑर्डर नाकारा",
        "start_delivery": "डिलिव्हरी सुरू करा",
        "update_status": "स्थिती अपडेट करा",

        "something_wrong": "काहीतरी चूक झाली",
        "try_again": "कृपया पुन्हा प्रयत्न करा",

        "no_orders": "कोणतेही ऑर्डर सापडले नाहीत",
        "no_requests": "कोणत्याही इंधन विनंत्या नाहीत"
    }
}

# ============================================================
# LANGUAGE HELPERS
# ============================================================

def get_current_language():
    language = session.get("language", "en")

    if language not in SUPPORTED_LANGUAGES:
        language = "en"

    return language


def get_translations():
    language = get_current_language()

    return TRANSLATIONS.get(
        language,
        TRANSLATIONS["en"]
    )


# ============================================================
# GLOBAL LANGUAGE CONTEXT
# ============================================================

@app.context_processor
def inject_language():
    language = get_current_language()

    return {
        "current_language": language,
        "language_names": LANGUAGE_NAMES,
        "t": get_translations()
    }


# ============================================================
# CUSTOMER LANGUAGE
# ============================================================

@app.route("/set_language", methods=["POST"])
def set_language():

    data = request.get_json(silent=True)

    if data:
        language = str(
            data.get("language", "en")
        ).strip().lower()
    else:
        language = str(
            request.form.get("language", "en")
        ).strip().lower()

    if language not in SUPPORTED_LANGUAGES:
        return jsonify({
            "success": False,
            "message": "Unsupported language"
        }), 400

    session["language"] = language

    return jsonify({
        "success": True,
        "language": language
    }), 200

# ============================================================
# PETROL LANGUAGE
# ============================================================

@app.route("/petrol_set_language", methods=["POST"])
def petrol_set_language():

    if "petrol" not in session:
        return jsonify({
            "success": False,
            "message": "Login required"
        }), 401

    data = request.get_json(silent=True)

    if data:
        language = str(
            data.get("language", "en")
        ).strip().lower()
    else:
        language = str(
            request.form.get("language", "en")
        ).strip().lower()

    if language not in SUPPORTED_LANGUAGES:
        return jsonify({
            "success": False,
            "message": "Unsupported language"
        }), 400

    session["language"] = language

    return jsonify({
        "success": True,
        "language": language
    }), 200

# =========================================================
# DATABASE MIGRATION
# =========================================================

def ensure_database_columns():

    conn = get_connection()
    cursor = conn.cursor()


    # =====================================================
    # ORDERS TABLE
    # =====================================================

    cursor.execute(
        "PRAGMA table_info(orders)"
    )

    order_columns = [
        row["name"]
        for row in cursor.fetchall()
    ]


    # =====================================================
    # ORDER COLUMNS
    # =====================================================

    order_columns_to_add = {

        # -------------------------------------------------
        # CUSTOMER LOCATION
        # -------------------------------------------------

        "customer_lat":
            "REAL",

        "customer_lon":
            "REAL",


        # -------------------------------------------------
        # PETROL PUMP LOCATION
        # -------------------------------------------------

        "pump_lat":
            "REAL",

        "pump_lon":
            "REAL",

        "pump_location_updated_at":
            "TEXT",


        # -------------------------------------------------
        # ORDER ACCEPT / CANCEL
        # -------------------------------------------------

        "accepted":
            "INTEGER DEFAULT 0",

        "cancelled":
            "INTEGER DEFAULT 0",

        "cancel_by":
            "TEXT",

        "cancel_reason":
            "TEXT",


        # -------------------------------------------------
        # DELIVERY
        # -------------------------------------------------

        "delivery_status":
            "TEXT DEFAULT 'Pending'",


        # -----------------------------------------------------
        # DELIVERY OTP
        # -----------------------------------------------------

        "delivery_otp":
            "TEXT",

        "delivery_otp_hash":
            "TEXT",

        "delivery_otp_expires_at":
            "TEXT",

        "delivery_otp_attempts":
            "INTEGER DEFAULT 0",

        "delivery_otp_verified":
            "INTEGER DEFAULT 0",

        "petrol_cleared":
            "INTEGER DEFAULT 0",

        "delivery_otp_created_at":
            "TEXT",


        # -------------------------------------------------
        # DELIVERY OTP
        # -------------------------------------------------

        "delivery_otp_hash":
            "TEXT",

        "delivery_otp_expires_at":
            "TEXT",

        "delivery_otp_attempts":
            "INTEGER DEFAULT 0",

        "delivery_otp_verified":
            "INTEGER DEFAULT 0",

        "delivery_otp_created_at":
            "TEXT",


        # -------------------------------------------------
        # PAYMENT
        # -------------------------------------------------

        "payment_method":
            "TEXT",

        "payment_status":
            "TEXT DEFAULT 'Pending'",


        # -------------------------------------------------
        # ORDER STATUS
        # -------------------------------------------------

        "status":
            "TEXT DEFAULT 'Pending Approval'",


        # =================================================
        # CLEAR ORDERS
        # =================================================

        # Customer ne apni current list se clear kiya
        "customer_cleared":
            "INTEGER DEFAULT 0",

        # Petrol pump ne apni current list se clear kiya
        "pump_cleared":
            "INTEGER DEFAULT 0",

        # Customer ne kis time clear kiya
        "customer_cleared_at":
            "TEXT",

        # Petrol pump ne kis time clear kiya
        "pump_cleared_at":
            "TEXT"

    }


    # =====================================================
    # ADD MISSING COLUMNS
    # =====================================================

    for column_name, column_type in (
        order_columns_to_add.items()
    ):

        if column_name not in order_columns:

            cursor.execute(
                f"""
                ALTER TABLE orders
                ADD COLUMN {column_name}
                {column_type}
                """
            )


    # =====================================================
    # PETROL PUMPS TABLE
    # =====================================================

    cursor.execute(
        "PRAGMA table_info(petrol_pumps)"
    )

    pump_columns = [
        row["name"]
        for row in cursor.fetchall()
    ]


    pump_columns_to_add = {

    "latitude":
        "REAL",

    "longitude":
        "REAL",

    "status":
        "TEXT DEFAULT 'Active'",

    "phone":
        "TEXT",

    "address":
        "TEXT",

    # =============================================
    # BANK DETAILS
    # =============================================

    "account_holder_name":
        "TEXT",

    "bank_name":
        "TEXT",

    "account_number":
        "TEXT",

    "ifsc_code":
        "TEXT",

    "upi_id":
        "TEXT"
    }

    for column_name, column_type in (
        pump_columns_to_add.items()
    ):

        if column_name not in pump_columns:

            cursor.execute(
                f"""
                ALTER TABLE petrol_pumps
                ADD COLUMN {column_name}
                {column_type}
                """
            )


    # Each pump can hide/reject a broadcast request for itself only.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pump_order_rejections (
            order_id INTEGER NOT NULL,
            petrol_pump_id INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (order_id, petrol_pump_id)
        )
    """)

    # =====================================================
    # SAVE DATABASE CHANGES
    # =====================================================

    conn.commit()

    conn.close()


# =========================================================
# RUN DATABASE MIGRATION
# =========================================================

try:

    ensure_database_columns()

    print(
        "Database migration completed successfully."
    )

except Exception as error:

    print(
        "Database migration warning:",
        error
    )


# =========================================================
# TEMPLATE LOADER
# =========================================================

app.jinja_loader = ChoiceLoader([
    FileSystemLoader(CUSTOMER_TEMPLATES),
    FileSystemLoader(PETROL_TEMPLATES)
])


# =========================================================
# STATIC FILES
# =========================================================

@app.route(
    "/static/<path:filename>",
    endpoint="static"
)
def static_files(filename):

    customer_file = os.path.join(
        CUSTOMER_STATIC,
        filename
    )

    if os.path.isfile(customer_file):

        return send_from_directory(
            CUSTOMER_STATIC,
            filename
        )


    petrol_file = os.path.join(
        PETROL_STATIC,
        filename
    )

    if os.path.isfile(petrol_file):

        return send_from_directory(
            PETROL_STATIC,
            filename
        )


    return "Static file not found", 404

# =========================================================
# LIVE REFRESH JAVASCRIPT
# =========================================================

@app.route("/live_refresh.js")
def live_refresh_js():

    return send_from_directory(
        CUSTOMER_STATIC,
        "live_refresh.js"
    )

# =========================================================
# SPLASH
# =========================================================

@app.route("/")
def splash():

    return render_template(
        "splash.html"
    )


# =========================================================
# SELECT ROLE
# =========================================================

@app.route("/select")
def select():

    return render_template(
        "select.html"
    )

# =========================================================
# PETROL REGISTER
# =========================================================

@app.route(
    "/petrol_register",
    methods=["GET", "POST"]
)
def petrol_register():

    # =====================================================
    # GET
    # =====================================================

    if request.method == "GET":

        return render_template(
            "petrol_register.html"
        )


    # =====================================================
    # GET FORM DATA
    # =====================================================

    pump_name = request.form.get(
        "pump_name",
        ""
    ).strip()


    owner_name = request.form.get(
        "owner_name",
        ""
    ).strip()


    username = request.form.get(
        "username",
        ""
    ).strip().lower()


    password = request.form.get(
        "password",
        ""
    )


    phone = request.form.get(
        "phone",
        ""
    ).strip()


    address = request.form.get(
        "address",
        ""
    ).strip()


    # =====================================================
    # VALIDATION
    # =====================================================

    if not all([
        pump_name,
        owner_name,
        username,
        password,
        phone,
        address
    ]):

        flash(
            "Please fill all fields.",
            "danger"
        )

        return redirect(
            url_for(
                "petrol_register"
            )
        )


    # =====================================================
    # DATABASE
    # =====================================================

    conn = get_connection()
    cursor = conn.cursor()


    try:

        # -------------------------------------------------
        # CHECK USERNAME
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT id
            FROM petrol_pumps
            WHERE username=?
            """,
            (
                username,
            )
        )


        existing_pump = cursor.fetchone()


        if existing_pump:

            flash(
                "Username already exists.",
                "danger"
            )

            return redirect(
                url_for(
                    "petrol_register"
                )
            )


        # -------------------------------------------------
        # HASH PASSWORD
        # -------------------------------------------------

        hashed_password = (
            generate_password_hash(
                password
            )
        )


        
        # Convert the registered pump address into coordinates
        pump_latitude, pump_longitude = get_coordinates_from_address(address)

        # -------------------------------------------------
        # CREATE PETROL PUMP
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO petrol_pumps
            (
                pump_name,
                owner_name,
                username,
                password,
                phone,
                address,
                latitude,
                longitude,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                pump_name,
                owner_name,
                username,
                hashed_password,
                phone,
                address,
                pump_latitude,
                pump_longitude,
                "Active"
            )
        )

        # -------------------------------------------------
        # GET NEW PUMP ID
        # -------------------------------------------------

        petrol_id = cursor.lastrowid


        # -------------------------------------------------
        # SAVE DATABASE
        # -------------------------------------------------

        conn.commit()


        # =================================================
        # TEMPORARY REGISTRATION SESSION
        # =================================================

        session["petrol_registration_id"] = petrol_id


        # =================================================
        # GO TO BANK DETAILS
        # =================================================

        return redirect(
            url_for(
                "petrol_bank_details",
                registration="1"
            )
        )


    except Exception as error:

        conn.rollback()


        print(
            "PETROL REGISTRATION ERROR:",
            error
        )


        flash(
            "Registration failed. Please try again.",
            "danger"
        )


        return redirect(
            url_for(
                "petrol_register"
            )
        )


    finally:

        conn.close()

# =========================================================
# PETROL PASSWORD CHECK
# =========================================================

def verify_petrol_password(
    stored_password,
    supplied_password
):

    if not stored_password:

        return False


    try:

        if stored_password.startswith(
            (
                "pbkdf2:",
                "scrypt:",
                "argon2:"
            )
        ):

            return check_password_hash(
                stored_password,
                supplied_password
            )

    except Exception:

        pass


    return stored_password == supplied_password


# =========================================================
# PETROL LOGIN
# =========================================================

@app.route(
    "/petrol_login",
    methods=["GET", "POST"]
)
def petrol_login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )


        conn = get_connection()
        cursor = conn.cursor()


        cursor.execute(
            """
            SELECT *
            FROM petrol_pumps
            WHERE username=?
            """,
            (username,)
        )


        pump = cursor.fetchone()

        conn.close()


        if (
            pump
            and pump["status"] == "Active"
            and verify_petrol_password(
                pump["password"],
                password
            )
        ):

            session.clear()

            session["petrol"] = pump["username"]

            session["petrol_id"] = pump["id"]

            session["pump_name"] = pump["pump_name"]

            session["language"] = "en"


            flash(
                "Login Successful.",
                "success"
            )

            return redirect(
                url_for("petrol_dashboard")
            )


        flash(
            "Invalid Username or Password.",
            "danger"
        )


    return render_template(
        "petrol_login.html"
    )


# =========================================================
# PETROL DASHBOARD
# =========================================================

@app.route("/dashboard")
def petrol_dashboard():

    if "petrol" not in session:

        return redirect(
            url_for("petrol_login")
        )


    conn = get_connection()
    cursor = conn.cursor()


    petrol_id = session.get(
        "petrol_id"
    )


    # -----------------------------------------------------
    # PETROL PUMP DETAILS
    # -----------------------------------------------------

    cursor.execute(
        """
        SELECT *
        FROM petrol_pumps
        WHERE id=?
        """,
        (
            petrol_id,
        )
    )

    pump = cursor.fetchone()


    if not pump:

        conn.close()

        session.clear()

        return redirect(
            url_for("petrol_login")
        )


    # -----------------------------------------------------
    # NEW REQUESTS
    # -----------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM orders
        WHERE petrol_pump_id=?
        AND status='Pending Approval'
        AND cancelled=0
        """,
        (
            petrol_id,
        )
    )

    new_requests = cursor.fetchone()[0]


    # -----------------------------------------------------
    # COMPLETED
    # -----------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM orders
        WHERE petrol_pump_id=?
        AND delivery_status='Completed'
        AND cancelled=0
        """,
        (
            petrol_id,
        )
    )

    completed_orders = cursor.fetchone()[0]


    # -----------------------------------------------------
    # TODAY EARNINGS
    # -----------------------------------------------------

    cursor.execute(
        """
        SELECT IFNULL(SUM(price), 0)
        FROM orders
        WHERE petrol_pump_id=?
        AND delivery_status='Completed'
        AND payment_status='Paid'
        AND cancelled=0
        AND DATE(order_date)=DATE('now')
        """,
        (
            petrol_id,
        )
    )

    today_earnings = cursor.fetchone()[0]


    # -----------------------------------------------------
    # CURRENT ORDERS
    # -----------------------------------------------------

    cursor.execute(
        """
        SELECT *
        FROM orders
        WHERE petrol_pump_id=?
        AND accepted=1
        AND cancelled=0
        AND delivery_status IN (
            'Preparing',
            'On The Way'
        )
        ORDER BY id DESC
        """,
        (
            petrol_id,
        )
    )

    current_orders = cursor.fetchall()


    conn.close()


    current_delivery = (
        current_orders[0]
        if current_orders
        else None
    )


    # -----------------------------------------------------
    # DASHBOARD
    # -----------------------------------------------------

    return render_template(
        "dashboard.html",

        pump=pump,

        pump_name=pump["pump_name"],

        new_requests=new_requests,

        completed_orders=completed_orders,

        current_delivery=current_delivery,

        today_earnings=today_earnings,

        current_orders=current_orders
    )

# =========================================================
# PETROL HOME
# =========================================================

@app.route("/petrol_home")
def petrol_home():

    if "petrol" not in session:

        return redirect(
            url_for("petrol_login")
        )

    return redirect(
        url_for("petrol_dashboard")
    )


@app.route("/index")
def index():

    if "petrol" not in session:

        return redirect(
            url_for("petrol_login")
        )

    return redirect(
        url_for("petrol_dashboard")
    )


# =========================================================
# PETROL PUMP ORDER HISTORY
# PART 3.3
# =========================================================

@app.route("/pump-order-history")
def pump_order_history():

    if "petrol_id" not in session:

        return redirect(
            url_for("petrol_login")
        )

    return render_template(
        "pump_order_history.html"
    )


# =========================================================
# PETROL PUMP ORDER HISTORY API
# =========================================================

@app.route("/api/pump-order-history")
def pump_order_history_api():

    if "petrol_id" not in session:

        return jsonify({
            "success": False,
            "message": "Login required"
        }), 401


    period = request.args.get(
        "period",
        "7"
    )


    if period not in ["7", "30"]:

        period = "7"


    days = int(period)


    conn = get_connection()
    cursor = conn.cursor()


    try:

        cursor.execute(
            f"""
            SELECT
                id,
                customer_email,
                phone,
                fuel,
                quantity,
                price,
                payment_status,
                status,
                delivery_status,
                order_date,
                pump_cleared

            FROM orders

            WHERE petrol_pump_id = ?

            AND (
                pump_cleared IS NULL
                OR pump_cleared = 0
            )

            AND datetime(order_date)
                >= datetime(
                    'now',
                    '-{days} days'
                )

            ORDER BY id DESC
            """,
            (
                session["petrol_id"],
            )
        )


        rows = cursor.fetchall()


        orders_list = []


        for row in rows:

            orders_list.append({

                "id":
                    row["id"],

                "customer_email":
                    row["customer_email"],

                "phone":
                    row["phone"],

                "fuel":
                    row["fuel"],

                "quantity":
                    row["quantity"],

                "price":
                    row["price"],

                "payment_status":
                    row["payment_status"],

                "status":
                    row["status"],

                "delivery_status":
                    row["delivery_status"],

                "order_date":
                    row["order_date"]

            })


        return jsonify({

            "success": True,

            "period":
                days,

            "orders":
                orders_list,

            "count":
                len(orders_list)

        })


    except Exception as error:

        print(
            "Pump order history error:",
            error
        )


        return jsonify({

            "success": False,

            "message":
                "Unable to load order history."

        }), 500


    finally:

        conn.close()


# =========================================================
# PETROL PUMP CLEAR ORDERS
# =========================================================

@app.route(
    "/pump-clear-orders",
    methods=["POST"]
)
def pump_clear_orders():

    if "petrol_id" not in session:

        return jsonify({
            "success": False,
            "message": "Login required"
        }), 401


    conn = get_connection()
    cursor = conn.cursor()


    try:

        cursor.execute(
            """
            UPDATE orders

            SET
                pump_cleared = 1,
                pump_cleared_at =
                    CURRENT_TIMESTAMP

            WHERE petrol_pump_id = ?

            AND (
                pump_cleared IS NULL
                OR pump_cleared = 0
            )
            """,
            (
                session["petrol_id"],
            )
        )


        cleared_count = cursor.rowcount


        conn.commit()


        return jsonify({

            "success": True,

            "cleared_count":
                cleared_count,

            "message":
                "Orders cleared successfully."

        })


    except Exception as error:

        conn.rollback()


        print(
            "Pump clear orders error:",
            error
        )


        return jsonify({

            "success": False,

            "message":
                "Unable to clear orders."

        }), 500


    finally:

        conn.close()


# =========================================================
# PETROL PUMP DOWNLOAD ORDERS CSV
# =========================================================

@app.route(
    "/pump-download-orders"
)
def pump_download_orders():

    if "petrol_id" not in session:

        return redirect(
            url_for("petrol_login")
        )


    period = request.args.get(
        "period",
        "7"
    )


    if period not in ["7", "30"]:

        period = "7"


    days = int(period)


    conn = get_connection()
    cursor = conn.cursor()


    try:

        cursor.execute(
            f"""
            SELECT
                id,
                customer_email,
                phone,
                fuel,
                quantity,
                price,
                payment_status,
                status,
                delivery_status,
                order_date

            FROM orders

            WHERE petrol_pump_id = ?

            AND (
                pump_cleared IS NULL
                OR pump_cleared = 0
            )

            AND datetime(order_date)
                >= datetime(
                    'now',
                    '-{days} days'
                )

            ORDER BY id DESC
            """,
            (
                session["petrol_id"],
            )
        )


        rows = cursor.fetchall()


        import csv
        import io


        output = io.StringIO()


        writer = csv.writer(
                output
            )


        # -------------------------------------------------
        # CSV HEADER
        # -------------------------------------------------

        writer.writerow([
            "Order ID",
            "Customer Email",
            "Customer Phone",
            "Fuel",
            "Quantity (L)",
            "Price",
            "Payment Status",
            "Order Status",
            "Delivery Status",
            "Order Date"
        ])


        # -------------------------------------------------
        # CSV DATA
        # -------------------------------------------------

        for row in rows:

            writer.writerow([

                row["id"],

                row["customer_email"],

                row["phone"],

                row["fuel"],

                row["quantity"],

                row["price"],

                row["payment_status"],

                row["status"],

                row["delivery_status"],

                row["order_date"]

            ])


        csv_data = output.getvalue()


        output.close()


        filename = (
            "petrol_orders_"
            + str(days)
            + "_days.csv"
        )


        return Response(

            csv_data,

            mimetype="text/csv",

            headers={
                "Content-Disposition":
                    "attachment; "
                    "filename=" +
                    filename,

                "Cache-Control":
                    "no-cache, no-store, "
                    "must-revalidate"
            }

        )


    except Exception as error:

        print(
            "CSV download error:",
            error
        )


        return "Unable to download orders.", 500


    finally:

        conn.close()

# =========================================================
# PETROL LOGOUT
# =========================================================

@app.route("/petrol_logout")
def petrol_logout():

    session.clear()

    flash(
        "Logout Successful.",
        "success"
    )

    return redirect(
        url_for("petrol_login")
    )


# =========================================================
# FORGOT PETROL PASSWORD
# =========================================================

@app.route(
    "/forgot_petrol_password",
    methods=["GET", "POST"]
)
def forgot_petrol_password():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip().lower()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        new_password = request.form.get(
            "new_password",
            ""
        )


        if not new_password:

            flash(
                "Please enter a new password.",
                "danger"
            )

            return redirect(
                url_for("forgot_petrol_password")
            )


        conn = get_connection()
        cursor = conn.cursor()


        cursor.execute(
            """
            SELECT *
            FROM petrol_pumps
            WHERE username=?
            AND phone=?
            """,
            (
                username,
                phone
            )
        )


        pump = cursor.fetchone()


        if not pump:

            conn.close()

            flash(
                "Invalid Username or Mobile Number.",
                "danger"
            )

            return redirect(
                url_for(
                    "forgot_petrol_password"
                )
            )


        hashed_password = generate_password_hash(
            new_password
        )


        cursor.execute(
            """
            UPDATE petrol_pumps
            SET password=?
            WHERE id=?
            """,
            (
                hashed_password,
                pump["id"]
            )
        )


        conn.commit()
        conn.close()


        flash(
            "Password Changed Successfully.",
            "success"
        )

        return redirect(
            url_for("petrol_login")
        )


    return render_template(
        "forgot_petrol_password.html"
    )


# =========================================================
# PETROL PROFILE
# =========================================================

@app.route("/petrol_profile", methods=["GET", "POST"])
def petrol_profile():
    if "petrol" not in session:
        return redirect(url_for("petrol_login"))

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        pump_name = request.form.get("pump_name", "").strip()
        owner_name = request.form.get("owner_name", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()

        if not all([pump_name, owner_name, phone, address]):
            conn.close()
            flash("Please fill all profile fields.", "danger")
            return redirect(url_for("petrol_edit_profile"))

        try:
            latitude, longitude = get_coordinates_from_address(address)

            cursor.execute("""
                UPDATE petrol_pumps
                SET pump_name = ?, owner_name = ?, phone = ?,
                    address = ?, latitude = ?, longitude = ?
                WHERE id = ?
            """, (
                pump_name, owner_name, phone, address,
                latitude, longitude, session["petrol_id"]
            ))

            conn.commit()
            flash("Pump profile updated successfully.", "success")

        except Exception:
            conn.rollback()
            app.logger.exception("Pump profile update failed")
            flash("Profile update failed. Please try again.", "danger")

        finally:
            conn.close()

        return redirect(url_for("petrol_profile"))

    cursor.execute(
        "SELECT * FROM petrol_pumps WHERE id = ?",
        (session["petrol_id"],)
    )
    pump = cursor.fetchone()

    cursor.execute(
        "SELECT COUNT(*) FROM orders WHERE petrol_pump_id = ?",
        (session["petrol_id"],)
    )
    total_orders = cursor.fetchone()[0]
    conn.close()

    if not pump:
        session.clear()
        return redirect(url_for("petrol_login"))

    if request.args.get("edit") == "1":
        return render_template("petrol_edit_profile.html", pump=pump)

    return render_template(
        "petrol_profile.html",
        pump=pump,
        total_orders=total_orders
    )

# =========================================================
# PETROL BANK DETAILS
# =========================================================

@app.route(
    "/petrol_bank_details",
    methods=["GET", "POST"]
)
def petrol_bank_details():

    # =====================================================
    # DETERMINE PETROL ID
    # =====================================================

    petrol_id = None


    # -----------------------------------------------------
    # FIRST-TIME REGISTRATION
    # -----------------------------------------------------

    if request.args.get("registration") == "1":

        petrol_id = session.get(
            "petrol_registration_id"
        )


    # -----------------------------------------------------
    # NORMAL EDIT FROM PROFILE
    # -----------------------------------------------------

    else:

        if "petrol" not in session:

            return redirect(
                url_for(
                    "petrol_login"
                )
            )


        petrol_id = session.get(
            "petrol_id"
        )


    # =====================================================
    # CHECK ID
    # =====================================================

    if not petrol_id:

        return redirect(
            url_for(
                "petrol_login"
            )
        )


    # =====================================================
    # DATABASE
    # =====================================================

    conn = get_connection()
    cursor = conn.cursor()


    try:

        # =================================================
        # SAVE BANK DETAILS
        # =================================================

        if request.method == "POST":

            account_holder_name = (
                request.form.get(
                    "account_holder_name",
                    ""
                ).strip()
            )


            bank_name = (
                request.form.get(
                    "bank_name",
                    ""
                ).strip()
            )


            account_number = (
                request.form.get(
                    "account_number",
                    ""
                ).strip()
            )


            ifsc_code = (
                request.form.get(
                    "ifsc_code",
                    ""
                ).strip().upper()
            )


            upi_id = (
                request.form.get(
                    "upi_id",
                    ""
                ).strip()
            )


            # ---------------------------------------------
            # REQUIRED FIELDS
            # ---------------------------------------------

            if not account_holder_name:

                flash(
                    "Account holder name is required.",
                    "danger"
                )

                return redirect(
                    url_for(
                        "petrol_bank_details",
                        registration=(
                            "1"
                            if session.get(
                                "petrol_registration_id"
                            )
                            else None
                        )
                    )
                )


            if not bank_name:

                flash(
                    "Bank name is required.",
                    "danger"
                )

                return redirect(
                    url_for(
                        "petrol_bank_details"
                    )
                )


            if not account_number:

                flash(
                    "Account number is required.",
                    "danger"
                )

                return redirect(
                    url_for(
                        "petrol_bank_details"
                    )
                )


            if not ifsc_code:

                flash(
                    "IFSC code is required.",
                    "danger"
                )

                return redirect(
                    url_for(
                        "petrol_bank_details"
                    )
                )


            # ---------------------------------------------
            # UPDATE BANK DETAILS
            # ---------------------------------------------

            cursor.execute(
                """
                UPDATE petrol_pumps

                SET
                    account_holder_name=?,
                    bank_name=?,
                    account_number=?,
                    ifsc_code=?,
                    upi_id=?

                WHERE id=?
                """,
                (
                    account_holder_name,
                    bank_name,
                    account_number,
                    ifsc_code,
                    upi_id,
                    petrol_id
                )
            )


            conn.commit()


            # =================================================
            # FIRST REGISTRATION COMPLETE
            # =================================================

            if session.get(
                "petrol_registration_id"
            ):

                session.pop(
                    "petrol_registration_id",
                    None
                )


                flash(
                    "Registration completed successfully. Please login.",
                    "success"
                )


                return redirect(
                    url_for(
                        "petrol_login"
                    )
                )


            # =================================================
            # NORMAL EDIT
            # =================================================

            flash(
                "Bank details updated successfully.",
                "success"
            )


            return redirect(
                url_for(
                    "petrol_profile"
                )
            )


        # =================================================
        # LOAD EXISTING DETAILS
        # =================================================

        cursor.execute(
            """
            SELECT *
            FROM petrol_pumps
            WHERE id=?
            """,
            (
                petrol_id,
            )
        )


        pump = cursor.fetchone()


        if not pump:

            session.pop(
                "petrol_registration_id",
                None
            )


            return redirect(
                url_for(
                    "petrol_login"
                )
            )


        # =================================================
        # SHOW PAGE
        # =================================================

        return render_template(
            "petrol_bank_details.html",
            pump=pump
        )


    except Exception as error:

        conn.rollback()


        print(
            "PETROL BANK DETAILS ERROR:",
            error
        )


        flash(
            "Unable to save bank details.",
            "danger"
        )


        return redirect(
            url_for(
                "petrol_bank_details"
            )
        )


    finally:

        conn.close()

# =========================================================
# PETROL SETTINGS
# =========================================================

@app.route("/petrol_settings")
def petrol_settings():

    if "petrol" not in session:

        return redirect(
            url_for("petrol_login")
        )


    return render_template(
        "petrol_settings.html"
    )


# =========================================================
# PETROL HELP
# =========================================================

@app.route("/petrol_help")
def petrol_help():

    if "petrol" not in session:

        return redirect(
            url_for("petrol_login")
        )


    return render_template(
        "petrol_help.html"
    )


# =========================================================
# CUSTOMER REGISTER
# =========================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        phone = request.form.get(
            "phone",
            ""
        ).strip()


        if not all([
            name,
            email,
            password,
            phone
        ]):

            flash(
                "Please fill all fields.",
                "danger"
            )

            return redirect(
                url_for("register")
            )


        conn = get_connection()
        cursor = conn.cursor()


        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE email=?
            """,
            (email,)
        )


        if cursor.fetchone():

            conn.close()

            flash(
                "Email already registered.",
                "danger"
            )

            return redirect(
                url_for("register")
            )


        hashed_password = generate_password_hash(
            password
        )


        cursor.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                password,
                phone
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                name,
                email,
                hashed_password,
                phone
            )
        )


        conn.commit()
        conn.close()

    return render_template(
        "register.html"
    )

# =========================================================
# CUSTOMER FORGOT PASSWORD
# =========================================================

@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():

    # =====================================================
    # SHOW FORGOT PASSWORD PAGE
    # =====================================================

    if request.method == "GET":

        return render_template(
            "forgot_password.html"
        )


    # =====================================================
    # GET FORM DATA
    # =====================================================

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    phone = request.form.get(
        "phone",
        ""
    ).strip()

    new_password = request.form.get(
        "new_password",
        ""
    )

    confirm_password = request.form.get(
        "confirm_password",
        ""
    )


    # =====================================================
    # VALIDATION
    # =====================================================

    if not email or not phone:

        flash(
            "Email and mobile number are required.",
            "danger"
        )

        return redirect(
            url_for("forgot_password")
        )


    if not new_password:

        flash(
            "New password is required.",
            "danger"
        )

        return redirect(
            url_for("forgot_password")
        )


    if new_password != confirm_password:

        flash(
            "Passwords do not match.",
            "danger"
        )

        return redirect(
            url_for("forgot_password")
        )


    if len(new_password) < 6:

        flash(
            "Password must be at least 6 characters.",
            "danger"
        )

        return redirect(
            url_for("forgot_password")
        )


    # =====================================================
    # DATABASE
    # =====================================================

    conn = get_connection()
    cursor = conn.cursor()


    try:

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE email = ?
            AND phone = ?
            LIMIT 1
            """,
            (
                email,
                phone
            )
        )


        user = cursor.fetchone()


        if not user:

            flash(
                "Email and mobile number do not match.",
                "danger"
            )

            return redirect(
                url_for("forgot_password")
            )


        # =================================================
        # UPDATE PASSWORD
        # =================================================

        hashed_password = (
            generate_password_hash(
                new_password
            )
        )


        cursor.execute(
            """
            UPDATE users
            SET password = ?
            WHERE id = ?
            """,
            (
                hashed_password,
                user["id"]
            )
        )


        conn.commit()


        flash(
            "Password reset successfully. Please login again.",
            "success"
        )


        return redirect(
            url_for("login")
        )


    except Exception as error:

        conn.rollback()

        print(
            "FORGOT PASSWORD ERROR:",
            error
        )


        flash(
            "Unable to reset password. Please try again.",
            "danger"
        )


        return redirect(
            url_for("forgot_password")
        )


    finally:

        conn.close()

# =========================================================
# CUSTOMER LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    # -----------------------------------------------------
    # CUSTOMER ALREADY LOGGED IN
    # -----------------------------------------------------

    if "user" in session:

        return redirect(
            url_for("home")
        )


    # -----------------------------------------------------
    # LOGIN FORM
    # -----------------------------------------------------

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()


        password = request.form.get(
            "password",
            ""
        )


        # -------------------------------------------------
        # DATABASE
        # -------------------------------------------------

        conn = get_connection()
        cursor = conn.cursor()


        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email=?
            """,
            (
                email,
            )
        )


        user = cursor.fetchone()


        conn.close()


        # -------------------------------------------------
        # CHECK LOGIN
        # -------------------------------------------------

        if (
            user
            and check_password_hash(
                user["password"],
                password
            )
        ):

            # ---------------------------------------------
            # CLEAR OLD CUSTOMER SESSION
            # ---------------------------------------------

            session.clear()


            # ---------------------------------------------
            # KEEP CUSTOMER LOGGED IN
            #
            # This makes the Flask session cookie
            # persistent even after browser restart.
            # ---------------------------------------------

            session.permanent = True


            # ---------------------------------------------
            # CUSTOMER DATA
            # ---------------------------------------------

            session["user"] = user["email"]


            session["customer_id"] = user["id"]


            session["customer_name"] =user["name"]


            session["language"] ="en"


            # ---------------------------------------------
            # LOGIN SUCCESS
            # ---------------------------------------------

            flash(
                "Login Successful.",
                "success"
            )


            return redirect(
                url_for("home")
            )


        # -------------------------------------------------
        # INVALID LOGIN
        # -------------------------------------------------

        flash(
            "Invalid Email or Password.",
            "danger"
        )


    return render_template(
        "login.html"
    )


# =========================================================
# CUSTOMER HOME
# =========================================================

@app.route("/home")
def home():

    if "user" not in session:

        return redirect(
            url_for("login")
        )


    return render_template(
        "home.html"
    )


# =========================================================
# CUSTOMER ORDER PAGE
# =========================================================


@app.route("/order/<fuel>")
def order(fuel):

    # DEBUG: Check customer session
    print("ORDER SESSION KEYS:", list(session.keys()))

    if "user" not in session:
        print("ORDER REDIRECT: Customer session missing")
        return redirect(url_for("login"))

    fuel = str(fuel).strip().lower()

    if fuel == "petrol":
        price = 111.21
        image = "fuel1.jpg"

    elif fuel == "diesel":
        price = 98.65
        image = "fuel2.png"

    else:
        flash("Invalid Fuel Type.", "danger")
        return redirect(url_for("home"))

    return render_template(
        "order.html",
        fuel=fuel.capitalize(),
        price=price,
        image=image
    )


# =========================================================
# CUSTOMER ORDERS PAGE
# =========================================================

@app.route("/orders")
def orders():

    if "user" not in session:

        return redirect(
            url_for("login")
        )


    conn = get_connection()
    cursor = conn.cursor()


    try:

        cursor.execute(
            """
            SELECT
                o.*,
                p.pump_name AS pump_name,
                p.phone AS pump_phone

            FROM orders o

            LEFT JOIN petrol_pumps p
                ON o.petrol_pump_id = p.id

            WHERE o.customer_email = ?

            AND (
                o.customer_cleared IS NULL
                OR o.customer_cleared = 0
            )

            ORDER BY o.id DESC
            """,
            (
                session["user"],
            )
        )


        orders_data = cursor.fetchall()


    finally:

        conn.close()


    return render_template(
        "orders.html",
        orders=orders_data
    )

# =========================================================
# CUSTOMER LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    # -----------------------------------------------------
    # COMPLETELY CLEAR CUSTOMER SESSION
    # -----------------------------------------------------

    session.clear()


    flash(
        "Logout Successful.",
        "success"
    )


    return redirect(
        url_for("login")
    )


# =========================================================
# CUSTOMER ANOTHER ACCOUNT
# =========================================================

@app.route("/another_account")
def another_account():

    # -----------------------------------------------------
    # CLEAR CURRENT CUSTOMER SESSION
    # -----------------------------------------------------

    session.clear()


    flash(
        "Please login with another account.",
        "success"
    )


    return redirect(
        url_for("login")
    )

# =========================================================
# CUSTOMER CHANGE PASSWORD
# =========================================================

@app.route("/change_password", methods=["GET", "POST"])
def change_password():

    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "GET":
        return render_template("change_password.html")

    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not current_password or not new_password or not confirm_password:
        flash("Please fill all password fields.", "danger")
        return redirect(url_for("change_password"))

    if len(new_password) < 6:
        flash("New password must be at least 6 characters.", "danger")
        return redirect(url_for("change_password"))

    if new_password != confirm_password:
        flash("New password and confirm password do not match.", "danger")
        return redirect(url_for("change_password"))

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT password FROM users WHERE email=?",
            (session["user"],)
        )
        user = cursor.fetchone()

        if not user or not check_password_hash(user["password"], current_password):
            flash("Current password is incorrect.", "danger")
            return redirect(url_for("change_password"))

        cursor.execute(
            "UPDATE users SET password=? WHERE email=?",
            (generate_password_hash(new_password), session["user"])
        )
        conn.commit()

        flash("Password changed successfully.", "success")
        return redirect(url_for("settings"))

    finally:
        conn.close()


# =========================================================
# CUSTOMER EDIT PROFILE
# =========================================================

@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():

    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    try:
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            phone = request.form.get("phone", "").strip()

            if not name or not phone.isdigit() or len(phone) != 10:
                flash("Please enter a valid name and 10 digit mobile number.", "danger")
                return redirect(url_for("edit_profile"))

            cursor.execute(
                "UPDATE users SET name=?, phone=? WHERE email=?",
                (name, phone, session["user"])
            )
            conn.commit()

            session["customer_name"] = name
            flash("Profile updated successfully.", "success")
            return redirect(url_for("profile"))

        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (session["user"],)
        )
        user = cursor.fetchone()

        if not user:
            session.clear()
            return redirect(url_for("login"))

        return render_template("edit_profile.html", user=user)

    finally:
        conn.close()


# =========================================================
# CUSTOMER PROFILE
# =========================================================

@app.route("/profile")
def profile():

    if "user" not in session:

        return redirect(
            url_for("login")
        )


    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE email=?
        """,
        (
            session["user"],
        )
    )


    user = cursor.fetchone()


    if not user:

        conn.close()

        session.clear()

        return redirect(
            url_for("login")
        )


    cursor.execute(
        """
        SELECT COUNT(*)
        FROM orders
        WHERE customer_email=?
        """,
        (
            session["user"],
        )
    )


    total_orders = cursor.fetchone()[0]


    conn.close()


    return render_template(
        "profile.html",
        user=user,
        total_orders=total_orders
    )


# =========================================================
# CUSTOMER SETTINGS
# =========================================================

@app.route("/settings")
def settings():

    if "user" not in session:

        return redirect(
            url_for("login")
        )


    return render_template(
        "settings.html"
    )


# =========================================================
# CUSTOMER NEED HELP
# =========================================================

@app.route("/need_help")
def need_help():

    if "user" not in session:

        return redirect(
            url_for("login")
        )


    return render_template(
        "need_help.html"
    )


def get_coordinates_from_address(address):
    """Convert a typed address into coordinates using OpenStreetMap."""
    url = (
        "https://nominatim.openstreetmap.org/search?"
        + urllib.parse.urlencode({
            "q": address,
            "format": "jsonv2",
            "limit": 1,
            "countrycodes": "in"
        })
    )

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "FuelOnCall/1.0 (address lookup)"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            results = json.loads(response.read().decode("utf-8"))

        if not results:
            return None, None

        latitude = float(results[0]["lat"])
        longitude = float(results[0]["lon"])

        return latitude, longitude

    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        ValueError,
        KeyError,
        TypeError
    ) as error:
        app.logger.warning("Address geocoding failed: %s", error)
        return None, None
  
  
def update_missing_pump_coordinates():
    import time

    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, pump_name, address
            FROM petrol_pumps
            WHERE latitude IS NULL
               OR longitude IS NULL
        """)

        pumps = cursor.fetchall()

        print("Pumps needing location update:", len(pumps))

        for pump in pumps:
            address = (pump["address"] or "").strip()

            if not address:
                print("Address missing for pump:", pump["pump_name"])
                continue

            print("Finding location:", pump["pump_name"], address)

            latitude, longitude = get_coordinates_from_address(address)

            if latitude is None or longitude is None:
                print("Location not found:", pump["pump_name"])
                continue

            cursor.execute("""
                UPDATE petrol_pumps
                SET latitude = ?, longitude = ?
                WHERE id = ?
            """, (latitude, longitude, pump["id"]))

            conn.commit()

            print(
                "Location saved:",
                pump["pump_name"],
                latitude,
                longitude
            )

            # Respect OpenStreetMap's public service limit
            time.sleep(1.1)

    except Exception as error:
        conn.rollback()
        print("PUMP LOCATION UPDATE ERROR:", error)

    finally:
        conn.close()


# =========================================================
# CUSTOMER PLACE ORDER
# =========================================================

@app.route("/place_order", methods=["POST"])
def place_order():
    if "user" not in session:
        return redirect(url_for("login"))

    fuel = request.form.get("fuel", "").strip().lower()
    quantity_text = request.form.get("quantity", "").strip()
    address = request.form.get("address", "").strip()
    phone = request.form.get("phone", "").strip()
    latitude_text = request.form.get("latitude", "").strip()
    longitude_text = request.form.get("longitude", "").strip()
    payment_method = request.form.get(
        "payment_method", "Cash on Delivery"
    ).strip()

    if fuel not in ("petrol", "diesel"):
        flash("Invalid fuel type.", "danger")
        return redirect(url_for("home"))

    if not quantity_text or not address or not phone:
        flash("Please fill all required fields.", "danger")
        return redirect(url_for("home"))

    try:
        quantity = float(quantity_text)
    except (ValueError, TypeError):
        flash("Invalid fuel quantity.", "danger")
        return redirect(url_for("home"))

    if quantity <= 0:
        flash("Quantity must be greater than 0.", "danger")
        return redirect(url_for("home"))

    # Customer coordinates are optional; pump selection no longer uses distance.
    customer_lat = None
    customer_lon = None
    try:
        if latitude_text and longitude_text:
            lat = float(latitude_text)
            lon = float(longitude_text)
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                customer_lat, customer_lon = lat, lon
    except (ValueError, TypeError):
        customer_lat = customer_lon = None

    if customer_lat is None or customer_lon is None:
        try:
            customer_lat, customer_lon = get_coordinates_from_address(address)
        except Exception as error:
            app.logger.warning("Address geocoding failed: %s", error)
            customer_lat = customer_lon = None

    fuel_price = 105.20 if fuel == "petrol" else 92.35
    total_price = quantity * fuel_price + 50

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id
            FROM petrol_pumps
            WHERE status = 'Active'
        """)
        active_pumps = cursor.fetchall()

        if not active_pumps:
            flash("No active petrol pump is available.", "danger")
            return redirect(url_for("home"))

        # Broadcast request: petrol_pump_id stays NULL until a pump claims it.
        cursor.execute("""
            INSERT INTO orders (
                customer_email, fuel, quantity, price, address, phone,
                payment_method, payment_status, status, petrol_pump_id,
                accepted, cancelled, cancel_by, cancel_reason,
                delivery_status, customer_lat, customer_lon,
                pump_lat, pump_lon, pump_location_updated_at,
                pump_cleared, customer_cleared
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL,
                0, 0, NULL, NULL, 'Pending', ?, ?, NULL, NULL, NULL,
                0, 0
            )
        """, (
            session["user"], fuel, quantity, total_price, address, phone,
            payment_method, "Pending", "Pending Approval",
            customer_lat, customer_lon
        ))

        order_id = cursor.lastrowid
        conn.commit()
        app.logger.info(
            "BROADCAST ORDER CREATED: order_id=%s eligible_pumps=%s",
            order_id, len(active_pumps)
        )
        flash("Order request sent to all active petrol pumps.", "success")
        return redirect(url_for("orders"))

    except Exception as error:
        conn.rollback()
        app.logger.exception("PLACE ORDER FAILED: %s", error)
        flash("Unable to place order. Please try again.", "danger")
        return redirect(url_for("home"))
    finally:
        conn.close()

# =========================================================
# CUSTOMER ORDERS LIVE API
# =========================================================

@app.route("/api/my_orders")
def my_orders_api():

    if "user" not in session:

        return jsonify({
            "success": False,
            "message": "Login required"
        }), 401


    conn = get_connection()
    cursor = conn.cursor()


    try:

        cursor.execute(
            """
            SELECT
                o.*,
                p.pump_name AS pump_name,
                p.phone AS pump_phone

            FROM orders o

            LEFT JOIN petrol_pumps p
                ON o.petrol_pump_id = p.id

            WHERE o.customer_email = ?

            AND (
                o.customer_cleared IS NULL
                OR o.customer_cleared = 0
            )

            ORDER BY o.id DESC
            """,
            (
                session["user"],
            )
        )


        rows = cursor.fetchall()


    finally:

        conn.close()


    result = []


    for row in rows:

        result.append({

            "id":
                row["id"],

            "customer_email":
                row["customer_email"],

            "fuel":
                row["fuel"],

            "quantity":
                row["quantity"],

            "price":
                row["price"],

            "address":
                row["address"],

            "phone":
                row["phone"],

            "accepted":
                row["accepted"],

            "cancelled":
                row["cancelled"],

            "status":
                row["status"],

            "delivery_status":
                row["delivery_status"],

            "payment_status":
                row["payment_status"],

            "payment_method":
                row["payment_method"],

            "pump_name":
                row["pump_name"],

            "pump_phone":
                row["pump_phone"],

            "delivery_otp":
                row["delivery_otp"],

        })


    return jsonify({

        "success": True,

        "orders":
            result

    })
# =========================================================
# PAYMENT
# =========================================================

@app.route(
    "/payment/<int:order_id>",
    endpoint="payment"
)
@app.route(
    "/payment_page/<int:order_id>",
    endpoint="payment_page"
)
def payment(order_id):

    if "user" not in session:

        return redirect(
            url_for("login")
        )


    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT *
        FROM orders
        WHERE id=?
        AND customer_email=?
        """,
        (
            order_id,
            session["user"]
        )
    )


    order_data = cursor.fetchone()


    conn.close()


    if not order_data:

        flash(
            "Order not found.",
            "danger"
        )

        return redirect(
            url_for("orders")
        )


    if order_data["accepted"] == 0:

        flash(
            "Waiting for Petrol Pump Approval.",
            "warning"
        )

        return redirect(
            url_for("orders")
        )


    if order_data["cancelled"] == 1:

        flash(
            "This order is cancelled.",
            "danger"
        )

        return redirect(
            url_for("orders")
        )


    return render_template(
        "payment.html",
        order=order_data
    )


# =========================================================
# PAYMENT SUCCESS
# =========================================================


@app.route(
    "/payment_success/<int:order_id>",
    methods=["POST"]
)
def payment_success(order_id):

    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Check that the order belongs to this customer.
        cursor.execute(
            """
            SELECT id, payment_status
            FROM orders
            WHERE id = ?
              AND customer_email = ?
              AND accepted = 1
              AND cancelled = 0
            """,
            (order_id, session["user"])
        )

        order = cursor.fetchone()

        if not order:
            flash("Order not found or not accepted.", "danger")
            return redirect(url_for("orders"))

        if order["payment_status"] == "Paid":
            flash("Payment is already marked as paid.", "info")
            return redirect(url_for("orders"))

        # Generate OTP after payment is marked successful.
        delivery_otp = str(
            secrets.randbelow(900000) + 100000
        )

        delivery_otp_hash = generate_password_hash(
            delivery_otp
        )

        now = datetime.now(timezone.utc)

        delivery_otp_created_at = now.isoformat()

        delivery_otp_expires_at = (
            now + timedelta(hours=24)
        ).isoformat()

        cursor.execute(
            """
            UPDATE orders
            SET
                payment_method = 'Online',
                payment_status = 'Paid',
                delivery_otp = ?,
                delivery_otp_hash = ?,
                delivery_otp_created_at = ?,
                delivery_otp_expires_at = ?,
                delivery_otp_attempts = 0,
                delivery_otp_verified = 0
            WHERE id = ?
              AND customer_email = ?
              AND accepted = 1
              AND cancelled = 0
              AND (payment_status IS NULL
                   OR payment_status != 'Paid')
            """,
            (
                delivery_otp,
                delivery_otp_hash,
                delivery_otp_created_at,
                delivery_otp_expires_at,
                order_id,
                session["user"]
            )
        )

        if cursor.rowcount != 1:
            conn.rollback()
            flash("Payment update failed.", "danger")
            return redirect(url_for("orders"))

        conn.commit()

        flash(
            "Payment successful. Your delivery OTP is ready.",
            "success"
        )

    except Exception:
        conn.rollback()
        app.logger.exception("Payment success error")
        flash("Payment update failed.", "danger")

    finally:
        conn.close()

    return redirect(url_for("orders"))


# =========================================================
# CUSTOMER CANCEL ORDER
# =========================================================

@app.route(
    "/cancel_order/<int:order_id>",
    methods=["GET", "POST"]
)
def cancel_order(order_id):

    if "user" not in session:

        return redirect(
            url_for("login")
        )


    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute(
        """
        UPDATE orders
        SET
            cancelled=1,
            status='Cancelled by Customer',
            cancel_by='Customer',
            delivery_status='Cancelled'
        WHERE id=?
        AND customer_email=?
        AND accepted=0
        AND cancelled=0
        """,
        (
            order_id,
            session["user"]
        )
    )


    changed = cursor.rowcount


    conn.commit()
    conn.close()


    if changed:

        flash(
            "Order Cancelled.",
            "success"
        )

    else:

        flash(
            "Order cannot be cancelled now.",
            "warning"
        )


    return redirect(
        url_for("orders")
    )


# =========================================================
# PETROL REQUESTS TEMPLATE ENDPOINT
# =========================================================

@app.route("/petrol_requests")
def petrol_requests():
    return fuel_requests()


# =========================================================
# PETROL CUSTOMERS
# =========================================================

@app.route("/customers")
def customers():

    if "petrol" not in session:
        return redirect(url_for("petrol_login"))

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT
                customer_email,
                MAX(phone) AS phone,
                COUNT(*) AS total_orders,
                MAX(order_date) AS last_order
            FROM orders
            WHERE petrol_pump_id = ?
            GROUP BY customer_email
            ORDER BY last_order DESC
        """, (session["petrol_id"],))

        return render_template(
            "customers.html",
            customers=cursor.fetchall()
        )
    finally:
        conn.close()


# =========================================================
# PETROL DAILY ORDERS
# =========================================================

@app.route("/daily_orders")
def daily_orders():

    if "petrol" not in session:
        return redirect(url_for("petrol_login"))

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT *
                 FROM orders

                WHERE petrol_pump_id = ?

                AND (
                    pump_cleared IS NULL
                    OR pump_cleared = 0
                )

                ORDER BY id DESC
        """, (session["petrol_id"],))

        return render_template(
            "daily_orders.html",
            orders=cursor.fetchall()
        )
    finally:
        conn.close()


# =========================================================
# PETROL CURRENT DELIVERIES
# =========================================================

@app.route("/current_deliveries")
def current_deliveries():

    if "petrol" not in session:

        return redirect(
            url_for("petrol_login")
        )


    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT *
        FROM orders
        WHERE petrol_pump_id=?
        AND accepted=1
        AND cancelled=0
        AND delivery_status IN (
            'Preparing',
            'On The Way'
        )
        ORDER BY id DESC
        """,
        (
            session["petrol_id"],
        )
    )


    deliveries = cursor.fetchall()


    conn.close()


    return render_template(
        "current_deliveries.html",
        deliveries=deliveries
    )


# =========================================================
# PETROL CURRENT DELIVERIES LIVE API
# =========================================================

@app.route("/api/current_deliveries")
def current_deliveries_api():

    if "petrol" not in session:
        return jsonify({
            "success": False,
            "message": "Login required"
        }), 401

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT
                id, customer_email, phone, fuel, quantity, price,
                address, accepted, cancelled, status,
                delivery_status, payment_status,
                customer_lat, customer_lon, pump_lat, pump_lon,
                pump_location_updated_at
            FROM orders
            WHERE petrol_pump_id = ?
              AND accepted = 1
              AND cancelled = 0
              AND delivery_status IN ('Preparing','On The Way')
            ORDER BY id DESC
        """, (session["petrol_id"],))

        rows = cursor.fetchall()
        deliveries = []
        for row in rows:
            deliveries.append({
                "id": row["id"],
                "customer_email": row["customer_email"],
                "phone": row["phone"],
                "fuel": row["fuel"],
                "quantity": row["quantity"],
                "price": row["price"],
                "address": row["address"],
                "accepted": row["accepted"],
                "cancelled": row["cancelled"],
                "status": row["status"],
                "delivery_status": row["delivery_status"],
                "payment_status": row["payment_status"],
                "customer_lat": row["customer_lat"],
                "customer_lon": row["customer_lon"],
                "pump_lat": row["pump_lat"],
                "pump_lon": row["pump_lon"],
                "pump_location_updated_at": row["pump_location_updated_at"]
            })

        return jsonify({
            "success": True,
            "deliveries": deliveries,
            "count": len(deliveries)
        })

    except Exception as error:
        print("CURRENT DELIVERIES API ERROR:", error)
        return jsonify({
            "success": False,
            "message": "Unable to load current deliveries."
        }), 500

    finally:
        conn.close()


# =========================================================
# PETROL FUEL REQUESTS
# =========================================================

@app.route("/fuel_requests")
def fuel_requests():
    if "petrol" not in session:
        return redirect(url_for("petrol_login"))

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT o.*
            FROM orders o
            WHERE o.cancelled = 0
              AND o.accepted = 0
              AND (o.petrol_pump_id IS NULL OR o.petrol_pump_id = ?)
              AND (
                  o.petrol_pump_id IS NULL
                  OR o.pump_cleared IS NULL
                  OR o.pump_cleared = 0
              )
              AND NOT EXISTS (
                  SELECT 1
                  FROM pump_order_rejections r
                  WHERE r.order_id = o.id
                    AND r.petrol_pump_id = ?
              )
            ORDER BY o.id DESC
        """, (session["petrol_id"], session["petrol_id"]))
        orders_data = cursor.fetchall()
        return render_template("fuel_requests.html", orders=orders_data)
    finally:
        conn.close()


# =========================================================
# SEND DELIVERY OTP SMS
# =========================================================

def send_delivery_otp_sms(
    customer_phone,
    delivery_otp
):

    authkey = os.environ.get(
        "MSG91_AUTHKEY",
        ""
    ).strip()


    template_id = os.environ.get(
        "MSG91_OTP_TEMPLATE_ID",
        ""
    ).strip()


    if not authkey:

        print(
            "MSG91_AUTHKEY is not configured."
        )

        return False


    if not template_id:

        print(
            "MSG91_OTP_TEMPLATE_ID "
            "is not configured."
        )

        return False


    # -----------------------------------------------------
    # CLEAN MOBILE NUMBER
    # -----------------------------------------------------

    phone = (
        str(customer_phone)
        .strip()
        .replace(" ", "")
        .replace("-", "")
    )


    if phone.startswith("+"):

        phone = phone[1:]


    if phone.startswith("0"):

        phone = "91" + phone[1:]


    elif len(phone) == 10:

        phone = "91" + phone


    # -----------------------------------------------------
    # MSG91 SEND OTP
    # -----------------------------------------------------

    query = urllib.parse.urlencode({

        "template_id":
            template_id,

        "mobile":
            phone,

        "authkey":
            authkey

    })


    url = (
        "https://control.msg91.com/api/v5/otp?"
        + query
    )


    payload = json.dumps({}).encode(
        "utf-8"
    )


    req = urllib.request.Request(

        url,

        data=payload,

        method="POST",

        headers={

            "Content-Type":
                "application/json",

            "Accept":
                "application/json"

        }

    )


    try:

        with urllib.request.urlopen(
            req,
            timeout=15
        ) as response:

            response_body = (
                response.read()
                .decode("utf-8")
            )


        print(
            "MSG91 OTP RESPONSE:",
            response_body
        )


        try:

            result = json.loads(
                response_body
            )

        except Exception:

            result = {}


        # MSG91 success response normally
        # contains type=success.

        if str(
            result.get("type", "")
        ).lower() == "success":

            return True


        # Some account/API responses may
        # use a message field.

        message = str(
            result.get(
                "message",
                ""
            )
        ).lower()


        if "success" in message:

            return True


        return False


    except urllib.error.HTTPError as error:

        error_body = ""

        try:

            error_body = (
                error.read()
                .decode("utf-8")
            )

        except Exception:

            pass


        print(
            "MSG91 HTTP ERROR:",
            error.code,
            error_body
        )


        return False


    except Exception as error:

        print(
            "MSG91 CONNECTION ERROR:",
            error
        )

        return False


# =========================================================
# ACCEPT ORDER
# =========================================================

@app.route(
    "/accept_order/<int:order_id>",
    methods=["GET", "POST"]
)
def accept_order(order_id):

    if "petrol" not in session:

        if request.headers.get(
            "X-Requested-With"
        ) == "XMLHttpRequest":

            return jsonify({
                "success": False,
                "message": "Login required"
            }), 401

        return redirect(
            url_for("petrol_login")
        )


    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT *
        FROM orders
        WHERE id=?
          AND (petrol_pump_id IS NULL OR petrol_pump_id=?)
        """,
        (
            order_id,
            session["petrol_id"]
        )
    )


    order_data = cursor.fetchone()


    if not order_data:

        conn.close()

        if request.headers.get(
            "X-Requested-With"
        ) == "XMLHttpRequest":

            return jsonify({
                "success": False,
                "message": "Order not found."
            }), 404

        flash(
            "Order not found.",
            "danger"
        )

        return redirect(
            url_for("fuel_requests")
        )


    if order_data["cancelled"] == 1:

        conn.close()

        if request.headers.get(
            "X-Requested-With"
        ) == "XMLHttpRequest":

            return jsonify({
                "success": False,
                "message":
                    "This order is already cancelled."
            }), 400

        flash(
            "This order is already cancelled.",
            "danger"
        )

        return redirect(
            url_for("fuel_requests")
        )


    if order_data["accepted"] == 1:

        conn.close()

        if request.headers.get(
            "X-Requested-With"
        ) == "XMLHttpRequest":

            return jsonify({
                "success": True,
                "message":
                    "Order is already accepted."
            })

        return redirect(
            url_for("current_deliveries")
        )


    # =====================================================
    # GET PUMP GPS
    # =====================================================

    cursor.execute(
        """
        SELECT latitude, longitude
        FROM petrol_pumps
        WHERE id=?
        """,
        (
            session["petrol_id"],
        )
    )


    pump = cursor.fetchone()


    pump_lat = None
    pump_lon = None


    if pump:

        try:

            if pump["latitude"] is not None:

                pump_lat = float(
                        pump["latitude"]
                    )


            if pump["longitude"] is not None:

                pump_lon = float(
                        pump["longitude"]
                    )

        except (
            ValueError,
            TypeError
        ):

            pump_lat = None
            pump_lon = None

   
    # =====================================================
    # ACCEPT ORDER + SAVE NEW OTP
    # =====================================================

    cursor.execute(
        """
        UPDATE orders
        SET
            petrol_pump_id = ?,
            accepted = 1,
            status = 'Accepted',
            delivery_status = 'Preparing',
            delivery_otp = NULL,
            delivery_otp_hash = NULL,
            delivery_otp_expires_at = NULL,
            delivery_otp_created_at = NULL,
            delivery_otp_attempts = 0,
            delivery_otp_verified = 0,
            pump_lat = ?,
            pump_lon = ?
        WHERE id = ?
          AND (petrol_pump_id IS NULL OR petrol_pump_id = ?)
          AND cancelled = 0
          AND accepted = 0
        """,
        (
            session["petrol_id"],
            pump_lat,
            pump_lon,
            order_id,
            session["petrol_id"]
        )
    )

    changed = cursor.rowcount

    if changed == 0:
        conn.rollback()
        conn.close()
        return jsonify({
            "success": False,
            "message": "Order could not be accepted."
        }), 400

    conn.commit()
    conn.close()


    # =====================================================
    # RESPONSE
    # =====================================================

    if request.headers.get(
        "X-Requested-With"
    ) == "XMLHttpRequest":

        return jsonify({

        "success": True,

        "message":
            "Order accepted. New delivery OTP generated.",

        "order_id":
            order_id,

        "accepted":
            1,

        "cancelled":
            0,

        "status":
            "Accepted",

        "delivery_status":
            "Preparing"

        })

    flash(
        "Order Accepted. New delivery OTP generated.",
        "success"
    )

    return redirect(
        url_for("current_deliveries")
    )

# =========================================================
# REJECT ORDER
# =========================================================

@app.route(
    "/reject_order/<int:order_id>",
    methods=["GET", "POST"]
)
def reject_order(order_id):
    if "petrol" not in session:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": False, "message": "Login required"}), 401
        return redirect(url_for("petrol_login"))

    pump_id = session["petrol_id"]
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id
            FROM orders
            WHERE id = ?
              AND (petrol_pump_id IS NULL OR petrol_pump_id = ?)
              AND accepted = 0
              AND cancelled = 0
        """, (order_id, pump_id))
        order_row = cursor.fetchone()
        if not order_row:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"success": False, "message": "Request is no longer available."}), 404
            flash("Request is no longer available.", "warning")
            return redirect(url_for("fuel_requests"))

        cursor.execute("""
            INSERT OR IGNORE INTO pump_order_rejections (order_id, petrol_pump_id)
            VALUES (?, ?)
        """, (order_id, pump_id))
        conn.commit()

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({
                "success": True,
                "message": "Request hidden from this pump only.",
                "order_id": order_id
            })

        flash("Request hidden from this pump. Other pumps can still accept it.", "success")
        return redirect(url_for("fuel_requests"))
    except Exception as error:
        conn.rollback()
        app.logger.exception("PUMP REQUEST REJECTION FAILED: %s", error)
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": False, "message": "Could not hide request."}), 500
        flash("Could not hide request.", "danger")
        return redirect(url_for("fuel_requests"))
    finally:
        conn.close()

# =========================================================
# PUMP CANCEL ORDER
# =========================================================

@app.route(
    "/pump_cancel_order/<int:order_id>",
    methods=["GET", "POST"]
)
def pump_cancel_order(order_id):

    if "petrol" not in session:

        if request.headers.get(
            "X-Requested-With"
        ) == "XMLHttpRequest":

            return jsonify({
                "success": False,
                "message": "Login required"
            }), 401

        return redirect(
            url_for("petrol_login")
        )


    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute(
        """
        UPDATE orders
        SET
            cancelled=1,
            status='Cancelled by Petrol Pump',
            cancel_by='Petrol Pump',
            delivery_status='Cancelled'
        WHERE id=?
        AND petrol_pump_id=?
        AND cancelled=0
        """,
        (
            order_id,
            session["petrol_id"]
        )
    )


    changed = cursor.rowcount


    conn.commit()
    conn.close()


    if request.headers.get(
        "X-Requested-With"
    ) == "XMLHttpRequest":

        if changed:

            return jsonify({
                "success": True,
                "message":
                    "Order cancelled.",
                "order_id":
                    order_id,
                "accepted": 0,
                "cancelled": 1,
                "status":
                    "Cancelled by Petrol Pump",
                "delivery_status":
                    "Cancelled"
            })


        return jsonify({
            "success": False,
            "message":
                "Order could not be cancelled."
        }), 400


    flash(
        "Order Cancelled.",
        "success"
    )


    return redirect(
        url_for("fuel_requests")
    )

# =========================================================
# DELIVERY OTP VERIFY PAGE
# =========================================================

@app.route(
    "/verify_delivery_otp/<int:order_id>",
    methods=["GET", "POST"]
)
def verify_delivery_otp(order_id):

    if "petrol" not in session:

        return redirect(
            url_for("petrol_login")
        )


    conn = get_connection()
    cursor = conn.cursor()


    try:

        cursor.execute(
            """
            SELECT
                id,
                petrol_pump_id,
                accepted,
                cancelled,
                delivery_status,
                delivery_otp_hash,
                delivery_otp_expires_at,
                delivery_otp_attempts,
                delivery_otp_verified

            FROM orders

            WHERE id=?

            AND petrol_pump_id=?

            LIMIT 1
            """,
            (
                order_id,
                session["petrol_id"]
            )
        )


        order_data = cursor.fetchone()


        if not order_data:

            flash(
                "Order not found.",
                "danger"
            )

            return redirect(
                url_for(
                    "current_deliveries"
                )
            )


        if order_data["cancelled"] == 1:

            flash(
                "This order is cancelled.",
                "warning"
            )

            return redirect(
                url_for(
                    "current_deliveries"
                )
            )


        if order_data["accepted"] != 1:

            flash(
                "Order is not accepted.",
                "warning"
            )

            return redirect(
                url_for(
                    "current_deliveries"
                )
            )


        if order_data[
            "delivery_otp_verified"
        ] == 1:

            flash(
                "Delivery OTP is already verified.",
                "success"
            )

            return redirect(
                url_for(
                    "current_deliveries"
                )
            )


        if request.method == "GET":

            return render_template(
                "verify_delivery_otp.html",
                order_id=order_id
            )


        # =================================================
        # OTP INPUT
        # =================================================

        otp = str(
            request.form.get(
                "otp",
                ""
            )
        ).strip()


        if (
            len(otp) != 6
            or not otp.isdigit()
        ):

            flash(
                "Enter a valid 6 digit OTP.",
                "danger"
            )

            return render_template(
                "verify_delivery_otp.html",
                order_id=order_id
            )


        # =================================================
        # ATTEMPT LIMIT
        # =================================================

        attempts = int(
            order_data[
                "delivery_otp_attempts"
            ] or 0
        )


        if attempts >= 5:

            flash(
                "Too many incorrect attempts. "
                "Please contact the customer.",
                "danger"
            )

            return render_template(
                "verify_delivery_otp.html",
                order_id=order_id
            )


        # =================================================
        # EXPIRY
        # =================================================

        expires_at = (
            order_data[
                "delivery_otp_expires_at"
            ]
        )


        if expires_at:

            try:

                expiry_time = (
                    datetime.fromisoformat(
                        expires_at
                    )
                )

                if datetime.utcnow() > expiry_time:

                    flash(
                        "Delivery OTP has expired.",
                        "danger"
                    )

                    return render_template(
                        "verify_delivery_otp.html",
                        order_id=order_id
                    )

            except Exception:

                pass


        # =================================================
        # VERIFY OTP
        # =================================================

        valid_otp = False


        try:

            valid_otp = (
                check_password_hash(
                    order_data[
                        "delivery_otp_hash"
                    ],
                    otp
                )
            )

        except Exception:

            valid_otp = False


        if not valid_otp:

            cursor.execute(
                """
                UPDATE orders

                SET
                    delivery_otp_attempts =
                    delivery_otp_attempts + 1

                WHERE id=?

                AND petrol_pump_id=?
                """,
                (
                    order_id,
                    session["petrol_id"]
                )
            )


            conn.commit()


            flash(
                "Incorrect delivery OTP.",
                "danger"
            )

            return render_template(
                "verify_delivery_otp.html",
                order_id=order_id
            )


        # =================================================
        # OTP CORRECT
        # =================================================

        cursor.execute(
            """
            UPDATE orders

            SET
                delivery_otp_verified=1,

                delivery_status='Completed',

                status='Completed'

            WHERE id=?

            AND petrol_pump_id=?

            AND accepted=1

            AND cancelled=0
            """,
            (
                order_id,
                session["petrol_id"]
            )
        )


        conn.commit()


        flash(
            "OTP verified. Delivery completed successfully.",
            "success"
        )


        return redirect(
            url_for(
                "current_deliveries"
            )
        )


    except Exception as error:

        conn.rollback()

        print(
            "DELIVERY OTP ERROR:",
            error
        )


        flash(
            "Unable to verify delivery OTP.",
            "danger"
        )


        return redirect(
            url_for(
                "current_deliveries"
            )
        )


    finally:

        conn.close()

# =========================================================
# UPDATE DELIVERY STATUS
# =========================================================

@app.route(
    "/update_order_status/<int:order_id>/<status>"
)
def update_order_status(
    order_id,
    status
):

    if "petrol" not in session:

        return redirect(
            url_for("petrol_login")
        )


    allowed = [
        "Preparing",
        "On The Way",
        "Completed"
    ]


    if status not in allowed:

        flash(
            "Invalid Status.",
            "danger"
        )

        return redirect(
            url_for("current_deliveries")
        )


    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute(
        """
        UPDATE orders
        SET
            delivery_status=?,
            status=?
        WHERE id=?
        AND petrol_pump_id=?
        AND accepted=1
        AND cancelled=0
        """,
        (
            status,
            status,
            order_id,
            session["petrol_id"]
        )
    )


    changed = cursor.rowcount


    conn.commit()
    conn.close()


    if changed:

        flash(
            "Delivery Status Updated.",
            "success"
        )

    else:

        flash(
            "Unable to update delivery status.",
            "warning"
        )


    if status == "Completed":

        return redirect(
            url_for("fuel_requests")
        )


    return redirect(
        url_for("current_deliveries")
    )


# =========================================================
# UPDATE PETROL PUMP GPS
# =========================================================

@app.route(
    "/update_pump_location",
    methods=["POST"]
)
def update_pump_location():

    if "petrol" not in session:

        return jsonify({
            "success": False,
            "message": "Login required"
        }), 401


    data = request.get_json(
        silent=True
    ) or {}


    try:

        latitude = float(
            data.get("latitude")
        )

        longitude = float(
            data.get("longitude")
        )

    except (
        ValueError,
        TypeError
    ):

        return jsonify({
            "success": False,
            "message": "Invalid GPS coordinates"
        }), 400


    if not (
        -90 <= latitude <= 90
        and -180 <= longitude <= 180
    ):

        return jsonify({
            "success": False,
            "message": "GPS coordinates out of range"
        }), 400


    conn = get_connection()
    cursor = conn.cursor()


    # -----------------------------------------------------
    # SAVE PUMP CURRENT LOCATION
    # -----------------------------------------------------

    cursor.execute(
        """
        UPDATE petrol_pumps
        SET
            latitude=?,
            longitude=?
        WHERE id=?
        """,
        (
            latitude,
            longitude,
            session["petrol_id"]
        )
    )


    # -----------------------------------------------------
    # SAVE LOCATION TO ACTIVE ORDERS
    # -----------------------------------------------------

    cursor.execute(
        """
        UPDATE orders
        SET
            pump_lat=?,
            pump_lon=?,
            pump_location_updated_at=datetime('now')
        WHERE petrol_pump_id=?
        AND accepted=1
        AND cancelled=0
        AND delivery_status IN (
            'Preparing',
            'On The Way'
        )
        """,
        (
            latitude,
            longitude,
            session["petrol_id"]
        )
    )


    conn.commit()
    conn.close()


    return jsonify({
        "success": True,
        "latitude": latitude,
        "longitude": longitude
    })


# =========================================================
# DELIVERY LOCATION
# =========================================================

@app.route(
    "/delivery_location/<int:order_id>"
)
def delivery_location(order_id):

    if (
        "user" not in session
        and "petrol" not in session
    ):

        return jsonify({
            "success": False,
            "message": "Login required"
        }), 401


    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT
            id,
            customer_email,
            phone,
            petrol_pump_id,
            customer_lat,
            customer_lon,
            pump_lat,
            pump_lon,
            address,
            delivery_status,
            accepted,
            cancelled,
            status
        FROM orders
        WHERE id=?
        """,
        (
            order_id,
        )
    )


    order_data = cursor.fetchone()


    conn.close()


    if not order_data:

        return jsonify({
            "success": False,
            "message": "Order not found"
        }), 404


    # -----------------------------------------------------
    # CUSTOMER ACCESS
    # -----------------------------------------------------

    if "user" in session:

        if (
            order_data["customer_email"]
            != session["user"]
        ):

            return jsonify({
                "success": False,
                "message": "Unauthorized"
            }), 403


    # -----------------------------------------------------
    # PUMP ACCESS
    # -----------------------------------------------------

    if "petrol" in session:

        if (
            order_data["petrol_pump_id"]
            != session["petrol_id"]
        ):

            return jsonify({
                "success": False,
                "message": "Unauthorized"
            }), 403


    return jsonify({

        "success": True,

        "order_id":
            order_data["id"],

        "customer": {

            "lat":
                order_data["customer_lat"],

            "lon":
                order_data["customer_lon"]

        },

        "pump": {

            "lat":
                order_data["pump_lat"],

            "lon":
                order_data["pump_lon"]

        },

        "address":
            order_data["address"],

        "phone":
            order_data["phone"],

        "delivery_status":
            order_data["delivery_status"],

        "status":
            order_data["status"],

        "accepted":
            order_data["accepted"],

        "cancelled":
            order_data["cancelled"]

    })


# =========================================================
# CUSTOMER ORDER LIVE STATUS API
# =========================================================

@app.route(
    "/order_status_api/<int:order_id>"
)
def order_status_api(order_id):

    if "user" not in session:

        return jsonify({
            "success": False,
            "message": "Login required"
        }), 401


    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT
            id,
            accepted,
            cancelled,
            status,
            delivery_status,
            payment_status,
            pump_lat,
            pump_lon,
            customer_lat,
            customer_lon,
            phone
        FROM orders
        WHERE id=?
        AND customer_email=?
        """,
        (
            order_id,
            session["user"]
        )
    )


    order_data = cursor.fetchone()


    conn.close()


    if not order_data:

        return jsonify({
            "success": False,
            "message": "Order not found"
        }), 404


    return jsonify({

        "success": True,

        "order_id":
            order_data["id"],

        "accepted":
            order_data["accepted"],

        "cancelled":
            order_data["cancelled"],

        "status":
            order_data["status"],

        "delivery_status":
            order_data["delivery_status"],

        "payment_status":
            order_data["payment_status"],

        "pump": {

            "lat":
                order_data["pump_lat"],

            "lon":
                order_data["pump_lon"]

        },

        "customer": {

            "lat":
                order_data["customer_lat"],

            "lon":
                order_data["customer_lon"]

        },

        "phone":
            order_data["phone"]

    })


# =========================================================
# PETROL REQUESTS LIVE API
# =========================================================

@app.route(
    "/petrol_orders_api"
)
def petrol_orders_api():

    if "petrol" not in session:

        return jsonify({
            "success": False,
            "message": "Login required"
        }), 401


    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT
            id,
            customer_email,
            fuel,
            quantity,
            price,
            address,
            phone,
            accepted,
            cancelled,
            status,
            delivery_status,
            payment_status,
            customer_lat,
            customer_lon
        FROM orders o
        WHERE (o.petrol_pump_id IS NULL OR o.petrol_pump_id=?)
          AND o.accepted=0
          AND o.cancelled=0
          AND (o.pump_cleared IS NULL OR o.pump_cleared=0)
          AND NOT EXISTS (
              SELECT 1 FROM pump_order_rejections r
              WHERE r.order_id=o.id
                AND r.petrol_pump_id=?
          )
        ORDER BY o.id DESC
        """,
        (
            session["petrol_id"],
            session["petrol_id"],
        )
    )


    rows = cursor.fetchall()


    conn.close()


    result = []


    for row in rows:

        result.append({

            "id":
                row["id"],

            "customer_email":
                row["customer_email"],

            "fuel":
                row["fuel"],

            "quantity":
                row["quantity"],

            "price":
                row["price"],

            "address":
                row["address"],

            "phone":
                row["phone"],

            "accepted":
                row["accepted"],

            "cancelled":
                row["cancelled"],

            "status":
                row["status"],

            "delivery_status":
                row["delivery_status"],

            "payment_status":
                row["payment_status"],

            "customer": {

                "lat":
                    row["customer_lat"],

                "lon":
                    row["customer_lon"]

            }

        })


    return jsonify({

        "success": True,

        "orders":
            result

    })

# =========================================================
# PETROL DASHBOARD LIVE API
# =========================================================

@app.route("/petrol_dashboard_api")
def petrol_dashboard_api():

    if "petrol" not in session:

        return jsonify({
            "success": False,
            "message": "Login required"
        }), 401


    conn = get_connection()
    cursor = conn.cursor()


    try:

        # =================================================
        # NEW REQUESTS
        # =================================================

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM orders o
            WHERE (o.petrol_pump_id IS NULL OR o.petrol_pump_id = ?)
              AND o.accepted=0
              AND o.status='Pending Approval'
              AND o.cancelled=0
              AND NOT EXISTS (
                  SELECT 1 FROM pump_order_rejections r
                  WHERE r.order_id=o.id AND r.petrol_pump_id=?
              )
            """,
            (
                session["petrol_id"],
                session["petrol_id"],
            )
        )

        new_requests = cursor.fetchone()[0]


        # =================================================
        # COMPLETED ORDERS
        # =================================================

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM orders
            WHERE petrol_pump_id=?
            AND delivery_status='Completed'
            AND cancelled=0
            """,
            (
                session["petrol_id"],
            )
        )

        completed_orders = cursor.fetchone()[0]


        # =================================================
        # TODAY EARNINGS
        # =================================================

        cursor.execute(
            """
            SELECT IFNULL(
                SUM(price),
                0
            )
            FROM orders
            WHERE petrol_pump_id=?
            AND delivery_status='Completed'
            AND payment_status='Paid'
            AND cancelled=0
            AND DATE(order_date)=DATE('now')
            """,
            (
                session["petrol_id"],
            )
        )

        today_earnings = cursor.fetchone()[0]


        # =================================================
        # CURRENT DELIVERIES
        # =================================================

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM orders
            WHERE petrol_pump_id=?
            AND accepted=1
            AND cancelled=0
            AND delivery_status IN (
                'Preparing',
                'On The Way'
            )
            """,
            (
                session["petrol_id"],
            )
        )

        current_delivery_count = cursor.fetchone()[0]


        return jsonify({

            "success": True,

            "new_requests":
                new_requests,

            "completed_orders":
                completed_orders,

            "current_delivery_count":
                current_delivery_count,

            "today_earnings":
                float(
                    today_earnings or 0
                )

        })


    finally:
        

        conn.close()

# =========================================================
# CUSTOMER PUMP LOCATIONS API
# =========================================================


@app.route("/api/pump_locations")
def pump_locations_api():

    if "user" not in session:
        return jsonify({
            "success": False,
            "message": "Login required"
        }), 401

    conn = get_connection()
    cursor = conn.cursor()

    try:
        station_type = request.args.get(
            "type", "petrol"
        ).lower()

        # Current database contains petrol_pumps.
        # CNG records need a real source/table before
        # they can be returned as CNG stations.
        if station_type not in ("petrol", "cng"):
            return jsonify({
                "success": False,
                "message": "Invalid station type"
            }), 400

        if station_type == "cng":
            return jsonify({
                "success": True,
                "pumps": [],
                "message": (
                    "CNG station data is not connected yet."
                )
            })

        cursor.execute("""
            SELECT
                id,
                pump_name,
                phone,
                address,
                latitude,
                longitude
            FROM petrol_pumps
            WHERE (status IS NULL OR status != 'Inactive')
              AND latitude IS NOT NULL
              AND longitude IS NOT NULL
            ORDER BY pump_name ASC
        """)

        rows = cursor.fetchall()
 
        pumps = []

        for row in rows:
            pumps.append({
                "id": row["id"],
                "pump_name": row["pump_name"],
                "phone": row["phone"],
                "address": row["address"],
                "latitude": row["latitude"],
                "longitude": row["longitude"]
            })

        return jsonify({
            "success": True,
            "pumps": pumps
        })

    except Exception as error:
        print("PUMP LOCATIONS API ERROR:", error)

        return jsonify({
            "success": False,
            "message": "Unable to load petrol pumps."
        }), 500

    finally:
        conn.close()


# =========================================================
# CUSTOMER CURRENT USER API
# =========================================================

@app.route(
    "/customer_profile_api"
)
def customer_profile_api():

    if "user" not in session:

        return jsonify({
            "success": False,
            "message": "Login required"
        }), 401


    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE email=?
        """,
        (
            session["user"],
        )
    )


    user = cursor.fetchone()


    conn.close()


    if not user:

        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404


    return jsonify({

        "success": True,

        "name":
            user["name"],

        "email":
            user["email"],

        "phone":
            user["phone"]

    })

# =========================================================
# CUSTOMER CLEAR ORDERS
# =========================================================

@app.route(
    "/customer_clear_orders",
    methods=["POST"]
)
def customer_clear_orders():

    if "user" not in session:

        return jsonify({
            "success": False,
            "message": "Login required"
        }), 401


    conn = get_connection()
    cursor = conn.cursor()


    try:

        cursor.execute(
            """
            UPDATE orders

            SET
                customer_cleared = 1,
                customer_cleared_at = CURRENT_TIMESTAMP

            WHERE customer_email = ?

            AND (
                customer_cleared IS NULL
                OR customer_cleared = 0
            )
            """,
            (
                session["user"],
            )
        )


        cleared_count = cursor.rowcount


        conn.commit()


        return jsonify({

            "success": True,

            "cleared_count":
                cleared_count,

            "message":
                "Orders cleared successfully."

        })


    except Exception as error:

        conn.rollback()

        print(
            "CUSTOMER CLEAR ERROR:",
            error
        )

        return jsonify({

            "success": False,

            "message":
                "Unable to clear orders."

        }), 500


    finally:

        conn.close()
        
# =========================================================
# PETROL PROFILE API
# =========================================================

@app.route(
    "/petrol_profile_api"
)
def petrol_profile_api():

    if "petrol" not in session:

        return jsonify({
            "success": False,
            "message": "Login required"
        }), 401


    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT
            id,
            pump_name,
            owner_name,
            username,
            phone,
            address,
            latitude,
            longitude,
            status
        FROM petrol_pumps
        WHERE id=?
        """,
        (
            session["petrol_id"],
        )
    )


    pump = cursor.fetchone()


    conn.close()


    if not pump:

        return jsonify({
            "success": False,
            "message": "Petrol pump not found"
        }), 404


    return jsonify({

        "success": True,

        "pump": {

            "id":
                pump["id"],

            "pump_name":
                pump["pump_name"],

            "owner_name":
                pump["owner_name"],

            "username":
                pump["username"],

            "phone":
                pump["phone"],

            "address":
                pump["address"],

            "latitude":
                pump["latitude"],

            "longitude":
                pump["longitude"],

            "status":
                pump["status"]

        }

    })

# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/health")
def health():

    return jsonify({
        "success": True,
        "app": "FuelOnCall",
        "status": "running"
    })


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    update_missing_pump_coordinates()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )