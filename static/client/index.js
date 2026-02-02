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
            //put_message_global_in_html();
            console.log(messages_global);
        }
    );
}

/*function put_message_global_in_html() {
    document.getElementById("messages").replaceChildren();

    var new_children = [];

    for (let i = 0; i < messages_global.length; i++) {
        var msg_element = new Element("div");
        msg_element.className = "message";
        msg_element.innerHTML =
            new_children.push();
    }
}*/