(function () {

    /* ------------------------------------------------------------
     * SPA Navigation
     * ------------------------------------------------------------ */
    const sections = document.querySelectorAll('.section');
    const buttons = document.querySelectorAll('.menu button');

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

            // CLOSE SIDEBAR IN MOBILE
            if (window.innerWidth <= 768) {
                document.getElementById('sidebar').classList.remove('open');
            }
        });
    });

    document.getElementById('hamburger').onclick = () =>
        document.getElementById('sidebar').classList.toggle('open');

    setActive(localStorage.getItem('nw_section') || 'map');


    /* ------------------------------------------------------------
     * CONFIG + SELECT ELEMENTS
     * ------------------------------------------------------------ */
    let CONFIG = null;

    const regionSelect = document.getElementById('regionSelect');
    const forecastSelect = document.getElementById('forecastSelect');
    const parameterSelect = document.getElementById('parameterSelect');
    const modelSelect = document.getElementById('modelSelect');
    const timeSelect = document.getElementById('timeSelect');
    const mapImage = document.getElementById('mapImage');


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
        const ftype = forecastSelect.value;
        const param = parameterSelect.value;
        const model = modelSelect.value;
        const ts = timeSelect.value;

        // If config doesn't have that region yet, keep static map visible
        if (!CONFIG || !CONFIG.regions || !CONFIG.regions[region]) {
            // show the base static map
            mapImage.src = "assets/maps/staticmap.png";
            return;
        }

        const filename = `${region}_${ftype}_${param}_${model}_${ts}.png`;
        mapImage.src = `assets/maps/${region}/${filename}`;
    }


    /* ------------------------------------------------------------
     * Dropdown Chain Loaders
     * ------------------------------------------------------------ */
    function isRegionPlaceholder(value) {
        if (!value) return true;

        const clean = value.toLowerCase().replace(/\s+/g, '');
        return clean.includes("selectregion") || clean.includes("selectregion(orclickonmap)");
    }
    function loadForecastTypes() {
        const region = regionSelect.value;
        if (isRegionPlaceholder(region)) {

            populate(forecastSelect, ["Type (Select a region first)"]);
            populate(parameterSelect, ["Parameter (Select a region first)"]);
            populate(modelSelect, ["Model (Select a region first)"]);
            populate(timeSelect, ["Time (Select a region first)"]);

            // Keep the base static map visible (do NOT clear src)
            mapImage.src = "assets/maps/staticmap.png";
            return;
        }
        const types = Object.keys(CONFIG.regions[region]?.forecast_types || { 'Select Forecast Types': {} });
        populate(forecastSelect, types);
        loadParameters();
    }

    function loadParameters() {
        const region = regionSelect.value;
        const type = forecastSelect.value;
        const params = Object.keys(CONFIG.regions[region].forecast_types[type]?.parameters || {});
        populate(parameterSelect, params);
        loadModels();
    }

    function loadModels() {
        const region = regionSelect.value;
        const type = forecastSelect.value;
        const models = CONFIG.regions[region].forecast_types[type]?.models || [];
        populate(modelSelect, models);
        loadTimes();
    }

    function loadTimes() {
        const region = regionSelect.value;
        const type = forecastSelect.value;
        const times = CONFIG.regions[region].forecast_types[type]?.timestamps || [];
        populate(timeSelect, times);
        updateMap();
    }


    /* ------------------------------------------------------------
     * Clickable Static Map Regions (lon/lat-based)
     * ------------------------------------------------------------ */

    // FULL MAP EXTENTS (these match your "Southeast Asia" extent)
    const MAP_LON_MIN = 90.0;
    const MAP_LON_MAX = 150.0;
    const MAP_LAT_MIN = -20.0;
    const MAP_LAT_MAX = 25.0;

    // region definitions: keys are the region identifiers (used as regionSelect.value)
    // bounds = [lon_min, lon_max, lat_min, lat_max]  (from your list)
    const regionDefs = [
        { id: "malacca_strait", display: "Malacca Strait", bounds: [95, 105, 0, 6] },
        { id: "south_china_sea", display: "South China Sea", bounds: [105.5, 121, 6, 25] },
        { id: "philippines", display: "Philippines", bounds: [116, 130, 6, 20] },
        { id: "andaman_gulf_thailand", display: "Andaman Sea & Gulf of Thailand", bounds: [90, 105.5, 6, 18] },
        { id: "java_nusa_tenggara", display: "Java - Nusa Tenggara", bounds: [103, 128, -13, -3] },
        { id: "western_indo", display: "Western Indo", bounds: [95, 120, -13, 6] },
        { id: "eastern_indo", display: "Eastern Indo", bounds: [120, 141, -13, 6] },
        { id: "indonesia", display: "Indonesia", bounds: [90, 141, -13, 6] },
        { id: "southeast_asia", display: "Southeast Asia", bounds: [90, 150, -20, 25] },
    ];

    // overlay element (must exist in HTML; you already added it)
    const overlay = document.getElementById("regionOverlay");

    // Compute lon/lat from click position on overlay
    function clickToLonLat(clickX, clickY) {
        const rect = overlay.getBoundingClientRect();
        const fracX = clickX / rect.width;   // 0..1 across image
        const fracY = clickY / rect.height;  // 0..1 down image

        const lon = MAP_LON_MIN + fracX * (MAP_LON_MAX - MAP_LON_MIN);
        // note: y fraction increases downward, while lat increases upward
        const lat = MAP_LAT_MAX - fracY * (MAP_LAT_MAX - MAP_LAT_MIN);

        return { lon, lat };
    }

    // click handler
    overlay.addEventListener("click", function (e) {
        const rect = overlay.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const clickY = e.clientY - rect.top;

        const { lon, lat } = clickToLonLat(clickX, clickY);
        console.log("click lon/lat:", lon.toFixed(3), lat.toFixed(3));

        // find matching region
        for (const r of regionDefs) {
            const [lonMin, lonMax, latMin, latMax] = r.bounds;
            if (lon >= lonMin && lon <= lonMax && lat >= latMin && lat <= latMax) {
                console.log("Clicked region:", r.id, r.display);

                // If CONFIG has the key, set it; otherwise set to slug anyway so user can see selection
                regionSelect.value = r.id;
                loadForecastTypes();
                return;
            }
        }

        console.log("No region matched.");
    });

    /* ------------------------------------------------------------
    * Hover Highlight + Label
    * ------------------------------------------------------------ */

    const regionHighlight = document.getElementById("regionHighlight");
    const regionLabel = document.getElementById("regionLabel");

    // Convert lon/lat box → pixel box on screen
    function regionBoxToPixels(bounds) {
        const [lonMin, lonMax, latMin, latMax] = bounds;

        // convert to fractional
        const fracX1 = (lonMin - MAP_LON_MIN) / (MAP_LON_MAX - MAP_LON_MIN);
        const fracX2 = (lonMax - MAP_LON_MIN) / (MAP_LON_MAX - MAP_LON_MIN);
        const fracY1 = (MAP_LAT_MAX - latMax) / (MAP_LAT_MAX - MAP_LAT_MIN);
        const fracY2 = (MAP_LAT_MAX - latMin) / (MAP_LAT_MAX - MAP_LAT_MIN);

        const w = overlay.clientWidth;
        const h = overlay.clientHeight;

        return {
            x: fracX1 * w,
            y: fracY1 * h,
            width: (fracX2 - fracX1) * w,
            height: (fracY2 - fracY1) * h
        };
    }

    overlay.addEventListener("mousemove", function(e) {

        const rect = overlay.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const { lon, lat } = clickToLonLat(x, y);

        let found = null;

        for (const r of regionDefs) {
            const [lonMin, lonMax, latMin, latMax] = r.bounds;
            if (lon >= lonMin && lon <= lonMax && lat >= latMin && lat <= latMax) {
                found = r;
                break;
            }
        }

        if (!found) {
            regionHighlight.style.display = "none";
            regionLabel.style.display = "none";
            return;
        }

        // convert region bounds → pixel highlight box
        const box = regionBoxToPixels(found.bounds);

        regionHighlight.style.display = "block";
        regionHighlight.style.left = box.x + "px";
        regionHighlight.style.top = box.y + "px";
        regionHighlight.style.width = box.width + "px";
        regionHighlight.style.height = box.height + "px";

        regionLabel.style.display = "block";
        regionLabel.textContent = found.display;
        regionLabel.style.left = (x + 12) + "px";
        regionLabel.style.top = (y + 12) + "px";
    });

    overlay.addEventListener("mouseleave", function() {
        regionHighlight.style.display = "none";
        regionLabel.style.display = "none";
    });


    /* ------------------------------------------------------------
     * Load CONFIG.json
     * ------------------------------------------------------------ */
    fetch("assets/config/config.json")
        .then(r => r.json())
        .then(json => {
            CONFIG = json;

            // If config does not include the region keys we use, add them as placeholders:
            // (so dropdown will show our region IDs)
            const cfgRegions = Object.assign({}, CONFIG.regions || {});
            for (const r of regionDefs) {
                if (!cfgRegions.hasOwnProperty(r.id)) {
                    // placeholder minimal structure for each region if missing
                    cfgRegions[r.id] = {
                        "forecast_types": {
                            "Weather": {
                                "parameters": {
                                    "rain": [],
                                    "sfc_temp": [],
                                    "rh": [],
                                    "mslp": []
                                },
                                "models": ["GFS", "ECMWF"],
                                "timestamps": []
                            },
                            "Wind and Waves": {
                                "parameters": {
                                    "surface_wind": [],
                                    "swh": [],
                                    "swell": []
                                },
                                "models": ["GFS", "WW3"],
                                "timestamps": []
                            }
                        }
                    };
                }
            }
            CONFIG.regions = cfgRegions;

            populate(regionSelect, Object.keys(CONFIG.regions));

            // if you prefer human readable labels in the select, replace options text here
            // (we keep option values as keys, so filenames use keys)
            [...regionSelect.options].forEach(opt => {
                const def = regionDefs.find(d => d.id === opt.value);
                if (def) opt.textContent = def.display;
            });

            // debug
            console.log("Available regions loaded:", Object.keys(CONFIG.regions));

            regionSelect.onchange = loadForecastTypes;
            forecastSelect.onchange = loadParameters;
            parameterSelect.onchange = loadModels;
            modelSelect.onchange = loadTimes;
            timeSelect.onchange = updateMap;

            loadForecastTypes();
        })
        .catch(err => {
            console.error("Failed to load config.json:", err);
            // still populate region dropdown from our regionDefs to allow clicks to work
            const tmp = {};
            regionDefs.forEach(d => tmp[d.id] = {});
            CONFIG = { regions: tmp };
            populate(regionSelect, Object.keys(CONFIG.regions));
            [...regionSelect.options].forEach(opt => {
                const def = regionDefs.find(d => d.id === opt.value);
                if (def) opt.textContent = def.display;
            });
        });

    document.querySelectorAll('.service-card').forEach(card => {
        card.addEventListener('click', () => {
            const target = card.dataset.target;
            localStorage.setItem('nw_section', target);
            setActive(target);
        });
    });

})();
