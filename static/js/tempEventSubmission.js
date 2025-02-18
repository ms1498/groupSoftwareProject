console.log("running script");
let form = document.getElementById("temp");
form.addEventListener("submit", (event) => {

    console.log("making json");
    const json = {
        "startKey": "aaaaa",
        "endKey": "aaaaa",
        "eventType": "racist",
        "organiser": "idk",
        "eventDate": "01-01-0001",
        "eventTime": "00:00:00",
        "eventLocation": "aaaaa",
        "expectedAttendance": 1,
        "actualAttendance": 2,
        "maximumAttendance": 3,
        "approved": false
    };

    fetch(window.location.href + "/post", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(json) });
});
console.log("event listener added");