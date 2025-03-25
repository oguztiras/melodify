document.addEventListener("DOMContentLoaded", function () {
    const messageContainer = document.querySelector("#messageContainer");

    messageContainer.addEventListener("click", function(event) {
        if (event.target.classList.contains("btn-delete")) {
            const messageId = event.target.parentElement.dataset.messageId;

            fetch(dltMsgUrl, {
                method: "POST",
                body: JSON.stringify({
                    messageId: messageId
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.log(data.error);
                    return;
                } else {
                    event.target.parentElement.style.display = "none";
                }
            })
            .catch(error => console.log("Error:", error));
        }
    });
});