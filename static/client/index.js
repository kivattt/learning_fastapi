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
                throw new Error("Response not OK");
            }
            return response.json();
        }
    ).then(
        response => {
            messages_global = response;
            put_message_global_in_html();
        }
    );
}

function put_message_global_in_html() {
    var root_messages = document.getElementById("messages");
    root_messages.innerHTML = "";

    for (let i = 0; i < messages_global.length; i++) {
        const msg = messages_global[i];

        let msg_elem = document.createElement("div");
        msg_elem.className = "message";

        let username_elem = document.createElement("div");
        if (msg.is_server_message) {
            username_elem.className = "server_username";
        } else {
            username_elem.className = "username";
        }
        username_elem.innerHTML = msg["author"].username;

        msg_elem.innerHTML = username_elem.outerHTML;
        msg_elem.innerHTML += msg["string"];

        root_messages.innerHTML += msg_elem.outerHTML;
    }
}

function send_message() {
    var input_text = document.getElementById("messagebox").value;

    if (input_text == null || input_text.length === 0) {
        return;
    }

    const author = "kivattt";

    const query_parameters = new URLSearchParams(window.location.search);
    fetch("/chat/" + query_parameters.get("chat_id") + "/new_message/" + author + "/" + input_text, {
        method: "POST"
    }).then(response => {
        if (!response.ok) {
            throw new Error("Response not OK");
        }
        return response.json();
    }).then(
        _ => {
            load_messages(); // Reload the messages because I'm lazy
            document.getElementById("messagebox").value = "";
        }
    )
}