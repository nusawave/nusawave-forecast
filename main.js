(function () {
    const sections = document.querySelectorAll('.section');
    const buttons = document.querySelectorAll('.menu button');


    function setActive(id) {
        sections.forEach(s => s.classList.remove('active'));
        let el = document.getElementById(id); if (el) el.classList.add('active');
        buttons.forEach(b => b.classList.toggle('active', b.dataset.section === id));
    }


    buttons.forEach(b => {
        b.addEventListener('click', () => {
            const sec = b.dataset.section;
            setActive(sec);
            localStorage.setItem('nw_section', sec);
        });
    });


    document.getElementById('hamburger').onclick = () =>
        document.getElementById('sidebar').classList.toggle('open');


    setActive(localStorage.getItem('nw_section') || 'map');


    // --- CONFIG LOADING ---
    let CONFIG = null;


    const regionSelect = document.getElementById('regionSelect');
    const forecastSelect = document.getElementById('modelSelect');
    const parameterSelect = document.getElementById('parameterSelect');
    const modelSelect = document.getElementById('parameterSelect');
    const timeSelect = document.getElementById('timeSelect');
    const mapImage = document.getElementById('mapImage');


    function populate(sel, items) { sel.innerHTML = ""; items.forEach(v => { let o = document.createElement('option'); o.value = v; o.textContent = v; sel.appendChild(o); }); }


    function updateMap() {
        const region = regionSelect.value;
        const ftype = forecastSelect.value;
        const param = parameterSelect.value;
        const model = modelSelect.value;
        const ts = timeSelect.value;


        const filename = `${region}_${ftype}_${param}_${model}_${ts}.png`;
        const path = `assets/maps/${region}/${filename}`;
        mapImage.src = path;
    }


    function loadForecastTypes() {
        const region = regionSelect.value;
        const types = Object.keys(CONFIG.regions[region].forecast_types || {});
        populate(forecastSelect, types);
        loadParameters();
    }


    function loadParameters() {
        const region = regionSelect.value;
        const type = forecastSelect.value;
        const params = Object.keys(CONFIG.regions[region].forecast_types[type].parameters || {});
        populate(parameterSelect, params);
        loadModels();
    }


    function loadModels() {
        const region = regionSelect.value;
        const type = forecastSelect.value;
        const models = CONFIG.regions[region].forecast_types[type].models || [];
        populate(modelSelect, models);
        loadTimes();
    }


    function loadTimes() {
        const region = regionSelect.value;
        const type = forecastSelect.value;
        const times = CONFIG.regions[region].forecast_types[type].timestamps || [];
        populate(timeSelect, times);
        updateMap();
    }

    fetch("assets/config/config.json").then(r => r.json()).then(json => {
        CONFIG = json;


        populate(regionSelect, Object.keys(CONFIG.regions));
        regionSelect.onchange = loadForecastTypes;
        forecastSelect.onchange = loadParameters;
        parameterSelect.onchange = loadModels;
        modelSelect.onchange = loadTimes;
        timeSelect.onchange = updateMap;


        loadForecastTypes();
    });
})();