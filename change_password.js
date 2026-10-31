function togglePassword(id, icon){

    let input = document.getElementById(id);

    if(input.type === "password"){

        input.type = "text";

        icon.innerHTML = "🙈";

    }
    else{

        input.type = "password";

        icon.innerHTML = "👁️";

    }

}

function validatePassword(){

    let current =
    document.getElementById("currentPassword").value.trim();

    let newPass =
    document.getElementById("newPassword").value.trim();

    let confirm =
    document.getElementById("confirmPassword").value.trim();

    if(current==""){

        alert("Enter Current Password");

        return false;

    }

    if(newPass.length < 6){

        alert("New Password must be at least 6 characters.");

        return false;

    }

    if(newPass != confirm){

        alert("New Password and Confirm Password do not match.");

        return false;

    }

    return true;

}