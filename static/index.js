window.addEventListener("hashchange", change_to_page_fragment);
window.addEventListener("DOMContentLoaded", change_to_page_fragment);

const urlFragmentToID = {
    "join": "join_chat_modal",
    "create": "create_chat_modal",
};

const idToUrlFragment = Object.fromEntries(
    Object.entries(urlFragmentToID).map(([k, v]) => [v, k])
);

function change_to_page_fragment() {
    if (!window.location.hash) {
        swap_homepage_contents_with_template(document.getElementById("homepage_modal"));
        return;
    }
    const urlFragment = window.location.hash.substring(1);

    const id = urlFragmentToID[urlFragment];
    if (id == null) {
        return;
    }

    swap_homepage_contents_with_template(document.getElementById(id));
}

function swap_homepage_contents_with_template(template) {
    const homepageModal = document.getElementById("homepage");
    homepageModal.replaceChildren(template.content.cloneNode(true));
}

function contains_forward_slash(name) {
    for (let i = 0; i < name.length; i++) {
        if (name[i] === '/') {
            return true;
        }
    }

    return false;
}

function create_chat_button() {
    const createChatModal = document.getElementById("create_chat_modal");
    window.location.hash = idToUrlFragment[createChatModal.id];
}

function create_chat() {
    const chatroom_name = document.getElementById("chatroom_name").value;
    // We can't allow forward-slashes, even percent-encoded ones (see "silly bug" section in README.md)
    if (contains_forward_slash(chatroom_name)) {
        // FIXME: Proper error message presented to the user
        return;
    }

    const chatroom_name_encoded = encodeURIComponent(chatroom_name);

    fetch("/chat/create_new/" + chatroom_name_encoded, {
        method: "POST"
    }).then(response => {
        if (!response.ok) {
            throw new Error("Response not OK")
        }
        return response.json();
    }).then(
        chatroom_id => {
            const query_parameters = new URLSearchParams({
                chat_id: chatroom_id,
            });

            window.location.href = "/static/client/?" + query_parameters;
        }
    )
}

function join_chat_button() {
    const joinChatModal = document.getElementById("join_chat_modal");
    window.location.hash = idToUrlFragment[joinChatModal.id];
}

function join_chat_from_invite_button() {
    const invite_code = document.getElementById("invite_code").value;
    // FIXME: Check if invite code is invalid, then show a descriptive error message

    const query_parameters = new URLSearchParams({
        chat_id: invite_code,
    });

    window.location.href = "/static/client/?" + query_parameters;
}