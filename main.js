(function () {

    /* ------------------------------------------------------------
     * SPA Navigation
     * ------------------------------------------------------------ */
    const sections = document.querySelectorAll('.section');
    const buttons  = document.querySelectorAll('.menu button');

    function setActive(id) {
        sections.forEach(s => s.classList.remove('active'));
        const el = document.getElementById(id);
        if (el) el.classList.add('active');

        buttons.forEach(b =>
            b.classList.toggle('active', b.dataset.section === id)
        );
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


    /* ------------------------------------------------------------
     * CONFIG + SELECT ELEMENTS
     * ------------------------------------------------------------ */
    let CONFIG = null;

    const regionSelect     = document.getElementById('regionSelect');
    const forecastSelect   = document.getElementById('forecastSelect');
    const parameterSelect  = document.getElementById('parameterSelect');
    const modelSelect      = document.getElementById('modelSelect');
    const timeSelect       = document.getElementById('timeSelect');
    const mapImage         = document.getElementById('mapImage');
    const regionMap        = document.getElementById('regionMap');


    /* ------------------------------------------------------------
     * Helper
     * ------------------------------------------------------------ */
    function populate(sel, items) {
        sel.innerHTML = "";
        items.forEach(v => {
            const o = document.createElement('option');
            o.value = v;
            o.textContent = v;
            sel.appendChild(o);
        });
    }


    /* ------------------------------------------------------------
     * Update Map Image
     * ------------------------------------------------------------ */
    function updateMap() {
        const region = regionSelect.value;
        const ftype  = forecastSelect.value;
        const param  = parameterSelect.value;
        const model  = modelSelect.value;
        const ts     = timeSelect.value;

        const filename = `${region}_${ftype}_${param}_${model}_${ts}.png`;
        mapImage.src = `assets/maps/${region}/${filename}`;
    }


    /* ------------------------------------------------------------
     * Dropdown Chain Loaders
     * ------------------------------------------------------------ */
    function loadForecastTypes() {
        const region = regionSelect.value;
        if (region === "Select Region") {

            populate(forecastSelect, ["Type (Region First)"]);
            populate(parameterSelect, ["Parameter (Region First)"]);
            populate(modelSelect, ["Model (Region First)"]);
            populate(timeSelect, ["Time (Region First)"]);

            mapImage.src = "";
            return;
        }
        const types  = Object.keys(CONFIG.regions[region]?.forecast_types || {'Select Forecast Types': {}});
        populate(forecastSelect, types);
        loadParameters();
    }

    function loadParameters() {
        const region = regionSelect.value;
        const type   = forecastSelect.value;
        const params = Object.keys(CONFIG.regions[region].forecast_types[type]?.parameters || {});
        populate(parameterSelect, params);
        loadModels();
    }

    function loadModels() {
        const region = regionSelect.value;
        const type   = forecastSelect.value;
        const models = CONFIG.regions[region].forecast_types[type]?.models || [];
        populate(modelSelect, models);
        loadTimes();
    }

    function loadTimes() {
        const region = regionSelect.value;
        const type   = forecastSelect.value;
        const times  = CONFIG.regions[region].forecast_types[type]?.timestamps || [];
        populate(timeSelect, times);
        updateMap();
    }


    /* ------------------------------------------------------------
     * Region Map Click Handler
     * ------------------------------------------------------------ */
    regionMap.onclick = () => {
        const regions = Object.keys(CONFIG.regions);
        let idx       = regions.indexOf(regionSelect.value);
        idx           = (idx + 1) % regions.length;
        regionSelect.value = regions[idx];
        loadForecastTypes();
    };


    /* ------------------------------------------------------------
     * Load CONFIG.json
     * ------------------------------------------------------------ */
    fetch("assets/config/config.json")
        .then(r => r.json())
        .then(json => {
            CONFIG = json;

            populate(regionSelect, Object.keys(CONFIG.regions));

            regionSelect.onchange    = loadForecastTypes;
            forecastSelect.onchange  = loadParameters;
            parameterSelect.onchange = loadModels;
            modelSelect.onchange     = loadTimes;
            timeSelect.onchange      = updateMap;

            loadForecastTypes();
        });

})();