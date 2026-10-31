function validateForm(){

    let name =
    document.querySelector("input[name='name']").value.trim();

    let phone =
    document.querySelector("input[name='phone']").value.trim();

    if(name==""){

        alert("Please enter your name.");

        return false;

    }

    if(phone==""){

        alert("Please enter your mobile number.");

        return false;

    }

    if(phone.length!=10){

        alert("Mobile number must be 10 digits.");

        return false;

    }

    if(isNaN(phone)){

        alert("Mobile number must contain only digits.");

        return false;

    }

    return true;

}