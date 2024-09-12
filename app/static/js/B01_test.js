window.addEventListener("pageshow", function (event) {
    var entries = performance.getEntriesByType("navigation");
    entries.forEach(function (entry) {
        if (entry.type == "back_forward") {
            alert("back");
        }
    });
});