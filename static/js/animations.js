document.addEventListener("DOMContentLoaded", () => {
    const indicator = document.getElementById("loadingIndicator");

    if (!indicator) return;

    let hideTimer;

    function showLoading(x, y) {
        // Clear any previous hide timer
        clearTimeout(hideTimer);

        // Make the indicator visible so its size can be measured
        indicator.classList.add("visible");

        // Get the size of the loading animation
        const indicatorWidth = indicator.offsetWidth;
        const indicatorHeight = indicator.offsetHeight;

        // Keep the animation inside the visible browser window
        const positionX = Math.min(
            x + 15,
            window.innerWidth - indicatorWidth - 10
        );

        const positionY = Math.min(
            y + 15,
            window.innerHeight - indicatorHeight - 10
        );

        // Position the animation where the user clicked
        indicator.style.left = `${Math.max(10, positionX)}px`;
        indicator.style.top = `${Math.max(10, positionY)}px`;

        // Hide it after a short time if the page does not navigate
        hideTimer = setTimeout(() => {
            indicator.classList.remove("visible");
        }, 3000);
    }

    // Detect clicks across the entire webpage
    document.addEventListener("click", (event) => {
        const clickedFeature = event.target.closest(
            "a[href], button, [role='button'], input[type='submit'], input[type='button']"
        );

        if (!clickedFeature) return;

        if (clickedFeature.disabled) return;

        // Ignore links that open new tabs or download files
        if (
            clickedFeature.tagName === "A" &&
            (
                clickedFeature.target === "_blank" ||
                clickedFeature.hasAttribute("download")
            )
        ) {
            return;
        }

        // Ignore links that only point to the same page
        if (clickedFeature.tagName === "A") {
            const url = new URL(
                clickedFeature.href,
                window.location.href
            );

            if (
                url.pathname === window.location.pathname &&
                url.search === window.location.search &&
                url.hash
            ) {
                return;
            }
        }

        showLoading(event.clientX, event.clientY);
    });

    // Handle form submissions
    document.addEventListener("submit", (event) => {
        if (event.target.checkValidity()) {
            showLoading(
                event.clientX || window.innerWidth / 2,
                event.clientY || window.innerHeight / 2
            );
        }
    });
});