document.addEventListener("DOMContentLoaded", () => {
    const panels = document.getElementById("liveMonitoringPanels");
    if (!panels) return;

    const endpoint = "/api/monitoring/dashboard";
    const refreshEveryMs = 15000;
    let refreshing = false;

    async function refreshMonitoring() {
        if (refreshing || document.hidden) return;
        refreshing = true;

        try {
            const response = await fetch(endpoint, {
                headers: { "Accept": "application/json" },
                cache: "no-store"
            });

            if (!response.ok) return;

            const data = await response.json();

            document.getElementById("liveTotalReviews").textContent = data.total_reviews;
            document.getElementById("liveTotalAnalyses").textContent = data.total_analyses;
            document.getElementById("liveFestivalCount").textContent = data.festival_count;
            document.getElementById("liveUnanalyzedReviews").textContent = data.unanalyzed_reviews;
            panels.innerHTML = data.monitoring_html;
        } catch (error) {
            console.warn("VibeCheck live refresh could not complete.", error);
        } finally {
            refreshing = false;
        }
    }

    window.setInterval(refreshMonitoring, refreshEveryMs);
    document.addEventListener("visibilitychange", () => {
        if (!document.hidden) refreshMonitoring();
    });
});
