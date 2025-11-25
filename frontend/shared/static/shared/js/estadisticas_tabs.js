document.addEventListener("DOMContentLoaded", function () {
    const tabs = document.querySelectorAll(".tab-btn");
    const contents = document.querySelectorAll(".tab-content");
    const activeTab = document.querySelector(".tab-btn.active");
    if (activeTab && activeTab.dataset.tab === "contabilidad" && typeof iniciarDashboardContabilidad === "function") {
        setTimeout(() => iniciarDashboardContabilidad(), 150);
    }
    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            tabs.forEach(t => t.classList.remove("active"));
            tab.classList.add("active");
            
            contents.forEach(c => c.classList.remove("active"));

            const target = document.getElementById(tab.dataset.tab);
            if (target) target.classList.add("active");

            setTimeout(() => {
                window.dispatchEvent(new Event("resize"));
                const tabName = tab.dataset.tab;
                if (tabName === "contabilidad" && typeof iniciarDashboardContabilidad === "function") {
                    iniciarDashboardContabilidad();
                }
                if (tabName === "alumnos" && typeof iniciarDashboardAlumnos === "function") {
                    iniciarDashboardAlumnos();
                }
                if (tabName === "administrativo" && typeof iniciarDashboardAdmin === "function") {
                    iniciarDashboardAdmin();
                }
            }, 150);
        });
    });
});
window.addEventListener("resize", () => {
    document.querySelectorAll(".chart").forEach(c => {
        const chart = echarts.getInstanceByDom(c);
        if (chart) chart.resize();
    });
});
