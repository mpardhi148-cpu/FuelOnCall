function validateRegister() {

    let name = document.getElementsByName("name")[0].value.trim();
    let email = document.getElementsByName("email")[0].value.trim();
    let password = document.getElementsByName("password")[0].value.trim();
    let phone = document.getElementsByName("phone")[0].value.trim();

    // Name Validation
    if (name == "") {
        alert("Please Enter Full Name");
        return false;
    }

    let namePattern = /^[A-Za-z ]+$/;

    if (!namePattern.test(name)) {
        alert("Name should contain only letters.");
        return false;
    }

    // Email Validation
    if (email == "") {
        alert("Please Enter Email");
        return false;
    }

    let emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailPattern.test(email)) {
        alert("Invalid Email Format");
        return false;
    }

    // Password Validation
    if (password == "") {
        alert("Please Enter Password");
        return false;
    }

    if (password.length < 6) {
        alert("Password must be at least 6 characters.");
        return false;
    }

    // Phone Validation
    if (phone == "") {
        alert("Please Enter Phone Number");
        return false;
    }

    let phonePattern = /^[0-9]{10}$/;

    if (!phonePattern.test(phone)) {
        alert("Phone Number must be exactly 10 digits.");
        return false;
    }

    return true;
}