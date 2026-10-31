document.addEventListener(
    "DOMContentLoaded",
    function () {


        // =================================================
        // ELEMENTS
        // =================================================

        const languageSelect =
            document.getElementById(
                "languageSelect"
            );


        const backProfileButton =
            document.getElementById(
                "backProfileButton"
            );


        const openHelpButton =
            document.getElementById(
                "openHelpButton"
            );


        const anotherAccountButton =
            document.getElementById(
                "anotherAccountButton"
            );


        // =================================================
        // LANGUAGE CHANGE
        // =================================================

        if (languageSelect) {

            languageSelect.addEventListener(
                "change",
                async function () {

                    const language =
                        this.value;


                    if (!language) {

                        return;

                    }


                    try {

                        const response =
                            await fetch(
                                "/set_language",
                                {
                                    method:
                                        "POST",

                                    headers: {
                                        "Content-Type":
                                            "application/json",

                                        "Accept":
                                            "application/json"
                                    },

                                    credentials:
                                        "same-origin",

                                    body:
                                        JSON.stringify({
                                            language:
                                                language
                                        })
                                }
                            );


                        const data =
                            await response.json();


                        if (
                            response.ok &&
                            data.success
                        ) {

                            window.location.reload();

                        } else {

                            alert(
                                data.message ||
                                "Unable to change language."
                            );

                        }


                    } catch (error) {

                        console.error(
                            "Language error:",
                            error
                        );


                        alert(
                            "Unable to change language."
                        );

                    }

                }
            );

        }


        // =================================================
        // ANOTHER ACCOUNT
        // =================================================

        if (
            anotherAccountButton
        ) {

            anotherAccountButton.addEventListener(
                "click",
                function () {

                    const confirmed =
                        confirm(
                            "Switch to another account?"
                        );


                    if (!confirmed) {

                        return;

                    }


                    window.location.href =
                        "/another_account";

                }
            );

        }


        // =================================================
        // BACK TO PROFILE
        // =================================================

        if (backProfileButton) {

            backProfileButton.addEventListener(
                "click",
                function () {

                    window.location.href =
                        "/profile";

                }
            );

        }


        // =================================================
        // NEED HELP
        // =================================================

        if (openHelpButton) {

            openHelpButton.addEventListener(
                "click",
                function () {

                    window.location.href =
                        "/need_help";

                }
            );

        }

    }
);