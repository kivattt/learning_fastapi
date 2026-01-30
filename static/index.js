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

function create_chat_button() {
    alert("Unimplemented");
}

function join_chat_button() {
    const joinChatModal = document.getElementById("join_chat_modal");
    window.location.hash = idToUrlFragment[joinChatModal.id];
}