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

    function goToSection(id) {
        setActive(id);
        localStorage.setItem('nw_section', id);
        if (window.innerWidth <= 768) {
            document.getElementById('sidebar').classList.remove('open');
        }
    }

    buttons.forEach(b => {
        b.addEventListener('click', () => {
            goToSection(b.dataset.section);
        });
    });

    document.getElementById('hamburger').onclick = () =>
        document.getElementById('sidebar').classList.toggle('open');

    document.querySelectorAll('.logo-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            goToSection(link.dataset.section || 'home');
        });
    });

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
    const prevBtn = document.getElementById('prevBtn');
    const playBtn = document.getElementById('playBtn');
    const nextBtn = document.getElementById('nextBtn');
    const overlay = document.getElementById('regionOverlay');
    const regionHighlight = document.getElementById('regionHighlight');
    const regionLabel = document.getElementById('regionLabel');

    // UI parameter labels -> backend file slugs
    const PARAM_SLUGS = {
        surface_wind: 'wind',
        swh: 'swh',
        swell: 'swell',
        rain: 'rainrate',
        sfc_temp: 'temp',
        rh: 'relhum',
        mslp: 'mslp',
        sst: 'seatemp',
        sss: 'seasalt',
        ssh: 'ssh',
    };

    const MODEL_DATASET = {
        GFS: 'gfswave',
        WW3: 'gfswave',
    };

    let playInterval = null;
    let pendingMapSrc = null;

    function showStaticMap() {
        pendingMapSrc = null;
        mapImage.src = 'assets/maps/staticmap.png';
    }

    mapImage.addEventListener('error', () => {
        const failed = pendingMapSrc || mapImage.getAttribute('src');
        if (!failed || failed.includes('staticmap.png')) return;
        console.warn('Map image missing, falling back to overview:', failed);
        pendingMapSrc = null;
        mapImage.src = 'assets/maps/staticmap.png';
    });


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
    function forecastMeta() {
        const region = regionSelect.value;
        const type = forecastSelect.value;
        return CONFIG?.regions?.[region]?.forecast_types?.[type] || {};
    }

    function timeIndexFromLabel(label) {
        const m = /^F(\d+)$/.exec(label || '');
        return m ? m[1].padStart(3, '0') : null;
    }

    function isPlaceholderOption(value) {
        if (!value) return true;
        return /^(Type|Parameter|Model|Time) \(/i.test(String(value));
    }

    function isStaticMapMode() {
        return isRegionPlaceholder(regionSelect.value);
    }

    function setRegionOverlayEnabled(enabled) {
        if (!overlay) return;
        overlay.style.pointerEvents = enabled ? 'auto' : 'none';
        overlay.style.cursor = enabled ? 'pointer' : 'default';
        if (!enabled) {
            regionHighlight.style.display = 'none';
            regionLabel.style.display = 'none';
        }
    }

    function updateMap() {
        const region = regionSelect.value;
        const param = parameterSelect.value;
        const model = modelSelect.value;
        const ts = timeSelect.value;

        setRegionOverlayEnabled(isStaticMapMode());

        if (isRegionPlaceholder(region) || isPlaceholderOption(param) || isPlaceholderOption(ts)) {
            showStaticMap();
            return;
        }

        const meta = forecastMeta();
        if (!meta.parameters || !Object.keys(meta.parameters).length) {
            showStaticMap();
            return;
        }

        const paramSlug = PARAM_SLUGS[param] || param;
        const timeIndex = timeIndexFromLabel(ts);
        if (!timeIndex) {
            showStaticMap();
            return;
        }

        const dataset = meta.dataset || MODEL_DATASET[model] || 'gfswave';
        pendingMapSrc = `assets/maps/${dataset}/${region}/${paramSlug}_${timeIndex}.webp`;
        mapImage.src = pendingMapSrc;
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

            setRegionOverlayEnabled(true);
            showStaticMap();
            return;
        }
        const types = Object.keys(CONFIG.regions[region]?.forecast_types || {});
        populate(forecastSelect, types.length ? types : ['Type (no data)']);
        loadParameters();
    }

    function loadParameters() {
        const region = regionSelect.value;
        const type = forecastSelect.value;
        if (isPlaceholderOption(type)) {
            populate(parameterSelect, ['Parameter (Select type first)']);
            populate(modelSelect, ['Model (Select type first)']);
            populate(timeSelect, ['Time (Select type first)']);
            updateMap();
            return;
        }
        const meta = CONFIG.regions[region]?.forecast_types?.[type];
        const params = Object.keys(meta?.parameters || {});
        populate(parameterSelect, params.length ? params : ['Parameter (no data)']);
        loadModels();
    }

    function loadModels() {
        const meta = forecastMeta();
        if (isPlaceholderOption(forecastSelect.value)) {
            populate(modelSelect, ['Model (Select type first)']);
            populate(timeSelect, ['Time (Select type first)']);
            updateMap();
            return;
        }
        const models = meta.models || [];
        populate(modelSelect, models.length ? models : ['GFS']);
        loadTimes();
    }

    function loadTimes() {
        const meta = forecastMeta();
        const param = parameterSelect.value;
        if (isPlaceholderOption(param)) {
            populate(timeSelect, ['Time (Select parameter first)']);
            updateMap();
            return;
        }
        const paramTimes = meta.parameters?.[param];
        const times = Array.isArray(paramTimes) && paramTimes.length
            ? paramTimes.filter(t => timeIndexFromLabel(t))
            : (meta.timestamps || []).filter(t => timeIndexFromLabel(t));
        populate(timeSelect, times.length ? times : ['Time (no data)']);
        updateMap();
    }

    function validTimeOptions() {
        return [...timeSelect.options].filter(o => timeIndexFromLabel(o.value));
    }

    function stepTime(delta) {
        const opts = validTimeOptions();
        if (opts.length <= 1) return;
        const current = timeSelect.options[timeSelect.selectedIndex];
        let idx = opts.indexOf(current);
        if (idx < 0) idx = 0;
        idx += delta;
        if (idx < 0 || idx >= opts.length) return;
        opts[idx].selected = true;
        updateMap();
    }

    function togglePlay() {
        if (playInterval) {
            clearInterval(playInterval);
            playInterval = null;
            playBtn.textContent = '▶️';
            return;
        }
        const opts = validTimeOptions();
        if (opts.length <= 1) return;
        playBtn.textContent = '⏸️';
        playInterval = setInterval(() => {
            const list = validTimeOptions();
            const current = timeSelect.options[timeSelect.selectedIndex];
            let idx = list.indexOf(current);
            if (idx < 0) idx = 0;
            if (idx >= list.length - 1) {
                list[0].selected = true;
            } else {
                list[idx + 1].selected = true;
            }
            updateMap();
        }, 800);
    }

    if (prevBtn) prevBtn.addEventListener('click', () => stepTime(-1));
    if (nextBtn) nextBtn.addEventListener('click', () => stepTime(1));
    if (playBtn) playBtn.addEventListener('click', togglePlay);

    const overviewBtn = document.getElementById('overviewBtn');
    if (overviewBtn) {
        overviewBtn.addEventListener('click', () => {
            if (playInterval) togglePlay();
            regionSelect.value = 'Select Region (or Click on Map)';
            loadForecastTypes();
        });
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

    function regionArea(bounds) {
        const [lonMin, lonMax, latMin, latMax] = bounds;
        return (lonMax - lonMin) * (latMax - latMin);
    }

    // Smallest bbox wins when regions overlap (e.g. Indonesia vs Java).
    const regionsBySpecificity = [...regionDefs].sort(
        (a, b) => regionArea(a.bounds) - regionArea(b.bounds)
    );

    function pickRegionAt(lon, lat) {
        for (const r of regionsBySpecificity) {
            const [lonMin, lonMax, latMin, latMax] = r.bounds;
            if (lon >= lonMin && lon <= lonMax && lat >= latMin && lat <= latMax) {
                return r;
            }
        }
        return null;
    }

    function regionSelectOptions() {
        const placeholder = "Select Region (or Click on Map)";
        const ordered = regionDefs.map(r => r.id);
        const extras = Object.keys(CONFIG?.regions || {}).filter(
            k => k !== placeholder && !ordered.includes(k)
        );
        return [placeholder, ...ordered, ...extras];
    }

    function populateRegionSelect() {
        populate(regionSelect, regionSelectOptions());
        [...regionSelect.options].forEach(opt => {
            const def = regionDefs.find(d => d.id === opt.value);
            if (def) opt.textContent = def.display;
        });
    }

    // overlay elements for static map region picking

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

    // click handler — only active on static overview map
    overlay.addEventListener("click", function (e) {
        if (!isStaticMapMode()) return;

        const rect = overlay.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const clickY = e.clientY - rect.top;

        const { lon, lat } = clickToLonLat(clickX, clickY);

        const match = pickRegionAt(lon, lat);
        if (match) {
            regionSelect.value = match.id;
            loadForecastTypes();
            return;
        }
    });

    /* ------------------------------------------------------------
    * Hover Highlight + Label (static map only)
    * ------------------------------------------------------------ */

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
        if (!isStaticMapMode()) return;

        const rect = overlay.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const { lon, lat } = clickToLonLat(x, y);
        const found = pickRegionAt(lon, lat);

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
                    cfgRegions[r.id] = {
                        forecast_types: {
                            'Wind and Waves': {
                                parameters: {
                                    surface_wind: [],
                                    swh: [],
                                    swell: [],
                                },
                                models: ['GFS'],
                                timestamps: [],
                                dataset: 'gfswave',
                            },
                        },
                    };
                }
            }
            CONFIG.regions = cfgRegions;

            populateRegionSelect();

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
            populateRegionSelect();
            regionSelect.onchange = loadForecastTypes;
            loadForecastTypes();
        });

    document.querySelectorAll('.service-card').forEach(card => {
        card.addEventListener('click', () => {
            const target = card.dataset.target;
            localStorage.setItem('nw_section', target);
            setActive(target);
        });
    });

})();
