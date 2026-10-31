document.addEventListener(
    "DOMContentLoaded",
    function () {

        const supportCallButton =
            document.getElementById(
                "supportCallButton"
            );


        if (supportCallButton) {

            supportCallButton.addEventListener(
                "click",
                function () {

                    /*
                     * tel: link browser/device ke
                     * available phone application ko
                     * call start karne ke liye use karega.
                     *
                     * Number ko apne actual support
                     * number se replace karna hai.
                     */

                    console.log(
                        "Support call requested."
                    );

                }
            );

        }

    }
);