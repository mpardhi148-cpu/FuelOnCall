document.addEventListener(
    "DOMContentLoaded",
    function () {


        // =================================================
        // BUTTONS
        // =================================================

        const settingsButton =
            document.getElementById(
                "settingsButton"
            );


        const helpButton =
            document.getElementById(
                "helpButton"
            );


        const myOrdersButton =
            document.getElementById(
                "myOrdersButton"
            );


        const logoutButton =
            document.getElementById(
                "logoutButton"
            );


        // =================================================
        // SETTINGS
        // =================================================

        if (settingsButton) {

            settingsButton.addEventListener(
                "click",
                function () {

                    window.location.href =
                        "/settings";

                }
            );

        }


        // =================================================
        // NEED HELP
        // =================================================

        if (helpButton) {

            helpButton.addEventListener(
                "click",
                function () {

                    window.location.href =
                        "/need_help";

                }
            );

        }


        // =================================================
        // MY ORDERS
        // =================================================

        if (myOrdersButton) {

            myOrdersButton.addEventListener(
                "click",
                function () {

                    window.location.href =
                        "/orders";

                }
            );

        }


        // =================================================
        // LOGOUT
        // =================================================

        if (logoutButton) {

            logoutButton.addEventListener(
                "click",
                function () {

                    const confirmed =
                        window.confirm(
                            "Are you sure you want to logout?"
                        );


                    if (!confirmed) {

                        return;
                    }


                    window.location.href =
                        "/logout";

                }
            );

        }

    }
);