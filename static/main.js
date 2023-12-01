console.log("Temo na área tiozão");

var action_list = document.querySelectorAll(".docker-event");

for (const item in action_list) {
    if (action_list.hasOwnProperty(item)) {
        const btn_action = action_list[item];
        const content = document.getElementById("content");
        const exec_cmd = document.getElementById("exec-cmd");

        btn_action.addEventListener("click", function (event) {
            event.preventDefault();

            var url = btn_action.getAttribute("data-url");
            url += "&command=" + exec_cmd.value;

            content.innerHTML = "";

            fetch(url)
                .then((response) => response.json())
                .then((data) => {
                    content.innerHTML =
                        url +
                        "\n------------------------------------------------------\n" +
                        data.message;
                });
            //  .then(response => response.text())
            //  .then(data => {content.innerHTML += data});
        });
    }
}

function getQueryParam(param) {
    const urlSearchParams = new URLSearchParams(window.location.search);
    return urlSearchParams.get(param);
}

const sortable = [
    { id: "sortIndex", param: "sortindex", caption: "#" },
    { id: "sortName", param: "sortname", caption: "Name" },
    { id: "sortStatus", param: "sortstatus", caption: "Status" },
    { id: "sortPorts", param: "sortports", caption: "Ports" },
];

sortable.map((e) => {
    const id = e.id;
    const param = e.param;
    const caption = e.caption;

    const statusLink = document.getElementById(id);

    const currentSortStatus = getQueryParam(param);

    statusLink.innerText = caption;
    if (currentSortStatus === "up") {
        statusLink.innerText += " ↑";
    } else if (currentSortStatus === "down") {
        statusLink.innerText += " ↓";
    }

    statusLink.addEventListener("click", function (event) {
        event.preventDefault();

        const newSortStatus = currentSortStatus === "up" ? "down" : "up";

        statusLink.href = `?${param}=${newSortStatus}`;

        window.location.href = statusLink.href;
    });
});
