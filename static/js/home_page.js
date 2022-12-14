// Wait for document to load
document.addEventListener("DOMContentLoaded", function(event) {

    // Get our button switcher
    var themeSwitcher = document.getElementById("theme-switcher");

    var theme = window.localStorage.currentTheme;

    if (theme == null || theme == "light") {
        document.documentElement.setAttribute("data-theme", "light");
    } else {
        document.documentElement.setAttribute("data-theme", "dark");
        themeSwitcher.src = "/static/image/dark.png";
        themeSwitcher.classList.toggle("invert");
        document.getElementById("search-icon").classList.toggle("invert");
    }

    // When our button gets clicked
    themeSwitcher.onclick = function() {
        // Get the current selected theme, on the first run
        // it should be `light`
        var currentTheme = document.documentElement.getAttribute("data-theme");

        // Switch between `dark` and `light`
        var switchToTheme = currentTheme === "dark" ? "light" : "dark";
        window.localStorage.currentTheme = switchToTheme;

        // Set our currenet theme to the new one
        document.documentElement.setAttribute("data-theme", switchToTheme);
        themeSwitcher.src = "/static/image/" + switchToTheme + ".png";
        themeSwitcher.classList.toggle("invert");
        document.getElementById("search-icon").classList.toggle("invert");
    }
});