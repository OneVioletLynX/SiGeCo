const tryFetch = async (url) => {
    try {
        const response = await fetch(url);
        return await response.json();
    } catch (ex) {
        alert(ex);
    }
};
const iniciarDashboardContabilidad = async () => {
    const data = await tryFetch("http://127.0.0.1:8000/api/seccion/contabilidad/");
    if (!data) {
        console.error("No se recibieron datos del servidor.");
        return;
    }
    // ==============================
    //          KPIS
    // ==============================
    const kpis = data.kpis;
    document.getElementById("ingresosMes").textContent = kpis.ingresos_mes;
    document.getElementById("ingresosAnio").textContent = kpis.ingresos_anio;
    document.getElementById("cuotasCoPen").textContent =
        `${kpis.cuotas_cobradas} / ${kpis.cuotas_estimadas_anio}`;
    document.getElementById("tasaMorosidad").textContent = kpis.tasa_morosidad;
    document.getElementById("alumnosAlDia").textContent = kpis.alumnos_al_dia;

    // ==============================
    //          CHARTS
    // ==============================
    const chartIngresos = echarts.init(document.getElementById("chartIngresos"));
    chartIngresos.setOption(data.charts.chartIngresos);
    chartIngresos.resize();
    const chartMediosPago = echarts.init(document.getElementById("chartMediosPago"))
    chartMediosPago.setOption(data.charts.chartMediosPago);
    chartMediosPago.resize();
    const chartDeudaPromedio = echarts.init(document.getElementById("chartDeudaPromedio"))
    chartDeudaPromedio.setOption(data.charts.chartDeudaPromedio);
    chartDeudaPromedio.resize();
    const chartDemoraPagos = echarts.init(document.getElementById("chartDemoraPagos"))
    chartDemoraPagos.setOption(data.charts.chartDemoraPagos);
    chartDemoraPagos.resize();
};

const iniciarDashboardAlumnos = async () => {
    const data = await tryFetch("http://127.0.0.1:8000/api/seccion/alumnos/");
    if (!data) {
        console.error("No se recibieron datos del servidor.");
        return;
    }
    // ==============================
    //          KPIS
    // ==============================
    const kpis = data.kpis;
    document.getElementById("alumnos_activos").textContent = kpis.alumnos_activos.value;
    console.log(document.getElementById("alumnos_activos"));
    document.getElementById("alumnos_egresados").textContent = kpis.alumnos_egresados.value;
    document.getElementById("alumnos_ingresantes").textContent = kpis.alumnos_ingresantes.value;
    document.getElementById("label_ingresantes").textContent = kpis.alumnos_ingresantes.label;
    if (kpis.tasa_retencion) {document.getElementById("tasaRetencion").textContent = kpis.tasa_retencion.value}
    if (kpis.prom_permanencia) {document.getElementById("promPermanencia").textContent = kpis.prom_permanencia.value}
    
    // ==============================
    //          CHARTS
    // ==============================
    const chartEgreIngre = echarts.init(document.getElementById("chartEgreIngre"))
    chartEgreIngre.setOption(data.charts.chartEgreIngre);
    chartEgreIngre.resize();
    const chartPorCarrera = echarts.init(document.getElementById("chartPorCarrera"))
    chartPorCarrera.setOption(data.charts.chartPorCarrera);
    chartPorCarrera.resize();
    const chartGenero = echarts.init(document.getElementById("chartGenero"))
    chartGenero.setOption(data.charts.chartGenero);
    chartGenero.resize();
    const chartEdad = echarts.init(document.getElementById("chartEdad"))
    chartEdad.setOption(data.charts.chartEdad);
    chartEdad.resize();
    const chartGeografia = echarts.init(document.getElementById("chartGeografia"))
    chartGeografia.setOption(data.charts.chartGeografia);
    chartGeografia.resize();
};

const iniciarDashboardAdmin = async () => {
    const data = await tryFetch("http://127.0.0.1:8000/api/seccion/administrativo/");
    if (!data) {
        console.error("No se recibieron datos del servidor.");
        return;
    }

    const kpis = data.kpis || {};
    const set  = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val ?? "—"; };
    set("kpiAltas",          kpis.altas);
    set("kpiModificaciones", kpis.modificaciones);
    set("kpiBajas",          kpis.bajas);
    set("kpiCobros",         kpis.cobros);

    const chartAltasMensuales = echarts.init(document.getElementById("chartAltasMensuales"));
    chartAltasMensuales.setOption(data.charts.chartAltasMensuales);
    chartAltasMensuales.resize();
};