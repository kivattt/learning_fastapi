window.onload = function () {
    load_messages();
}

var messages_global;

function load_messages() {
    const query_parameters = new URLSearchParams(window.location.search);
    fetch("/chat/" + query_parameters.get("chat_id") + "/messages",
        {
            method: "POST",
        }).then(response => {
            if (!response.ok) {
                throw new Error("God fucking damnit")
            }
            return response.json();
        }
    ).then(
        response => {
            messages_global = response;
            console.log(messages_global);
        }
    );
}