import sys
import importlib
import cartopy.crs as ccrs
from pathlib import Path
import numpy as np

def _ensure_project_root():
    """
    Ensure that the project root (directory containing 'plotter/')
    is available in sys.path.
    """
    current_file = Path(__file__).resolve()

    root = current_file.parents[2]

    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

def get_projection(name):
    if name == "mercator":
        return ccrs.Mercator()
    elif name == "plate":
        return ccrs.PlateCarree()
    elif name == "northpolar":
        return ccrs.NorthPolarStereo()
    return ccrs.PlateCarree()

def load_model_params(dataset):
    _ensure_project_root()

    module_name = f"plotter.modelparams.{dataset}"

    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        raise ValueError(
            f"[ERROR] Dataset selector '{dataset}' not found.\n"
            f"Expected at: plotter/modelparams/{dataset}.py"
        )

    if not hasattr(module, "VARIABLE_MAP"):
        raise ValueError(
            f"[ERROR] Dataset module '{module_name}' does not define VARIABLE_MAP"
        )

    return module.VARIABLE_MAP

def select_time(ds, cfg):
    if cfg.time_index is not None:
        return ds.isel(time=cfg.time_index)
    if cfg.time_value is not None:
        return ds.sel(time=cfg.time_value, method="nearest")
    return ds

def select_bbox(data, cfg):
    if not cfg.bbox:
        return data
    minlon, maxlon, minlat, maxlat = cfg.bbox
    return data.sel(lon=slice(minlon, maxlon), lat=slice(minlat, maxlat))

def select_level(data, cfg):
    if cfg.level is None:
        return data

    # generic logic
    for dim in ["isobaricInhPa", "level", "pressure"]:
        if dim in data.dims:
            return data.sel({dim: cfg.level}, method="nearest")

    return data

def select_depth(data, cfg):
    if cfg.depth is None:
        return data

    for dim in ["depth", "z"]:
        if dim in data.dims:
            return data.sel({dim: cfg.depth}, method="nearest")

    return data

def get_dataset_url(dataset, cycle):
    y = cycle[:4]
    m = cycle[4:6]
    d = cycle[6:8]
    h = cycle[8:10]

    if dataset == "gfsatmos":
        return f"https://nomads.ncep.noaa.gov/dods/gfs_0p25/gfs{y}{m}{d}/gfs_0p25_{h}z"
    
    if dataset == "gfswave":
        return f"https://nomads.ncep.noaa.gov/dods/wave/gfswave/{y}{m}{d}/gfswave.global.0p25_{h}z"
    
    if dataset == "ecmwfatmos":
        return f"https://example.ecmwf.int/era5_{y}{m}{d}_{h}.nc"   # placeholder
    
    if dataset == "ecmwfwave":
        return f"https://example.ecmwf.int/era5_wave_{y}{m}{d}_{h}.nc"
    
    if dataset == "hycom":
        return f"https://hycom.org/dods/datasets/global_analysis_forecast/{y}{m}{d}.nc"
    
    if dataset == "cmems":
        return f"https://my.cmems-duacs.org/dods/global-analysis-forecast-phy/{y}{m}{d}.nc"

    raise ValueError("Unknown dataset source")

def deep_update(base: dict, updates: dict):
    """
    Recursively merge two dictionaries.
    Values in updates override those in base.
    """
    for k, v in updates.items():
        if (
            k in base 
            and isinstance(base[k], dict) 
            and isinstance(v, dict)
        ):
            deep_update(base[k], v)
        else:
            base[k] = v
    return base

def compute_quiver_params(lat, lon, cfg):
    lat = np.asarray(lat)
    lon = np.asarray(lon)

    # 1. Domain range
    lat_range = float(lat.max() - lat.min())
    lon_range = float(lon.max() - lon.min())

    # 2. Robust resolution estimate
    resolution = float(np.median(np.diff(lon)))

    # 3. Estimate grid count
    n_lat = lat_range / resolution
    n_lon = lon_range / resolution
    grid_count = np.sqrt(n_lat * n_lon)

    # 4. Skip based on grid count
    skip_factor = cfg.quiver.get("skipfactor", 30)
    skip = max(1, int(grid_count / skip_factor))

    # 5. Geometric correction of area
    lat_mid = float((lat.max() + lat.min()) / 2)
    effective_area = lat_range * lon_range * np.cos(np.deg2rad(lat_mid))
    effective_area = max(effective_area, 1e-6)

    # 6. Scale
    scale_factor = cfg.quiver.get("scalefactor", 40)
    scale = scale_factor / np.sqrt(effective_area)

    # 7. Stabilize scale to realistic limits
    scale = float(np.clip(scale, 60, 200))

    print(skip, scale)
    return skip, scale