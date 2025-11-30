import importlib
import cartopy.crs as ccrs

def get_projection(name):
    if name == "mercator":
        return ccrs.Mercator()
    elif name == "plate":
        return ccrs.PlateCarree()
    elif name == "northpolar":
        return ccrs.NorthPolarStereo()
    return ccrs.PlateCarree()

def apply_bbox(ax, bbox):
    if bbox:
        min_lon, max_lon, min_lat, max_lat = bbox
        ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())

def load_model_params(dataset):
    try:
        module = importlib.import_module(f"plotter.modelparams.{dataset}")
        return module.VARIABLE_MAP
    except ModuleNotFoundError:
        raise ValueError(f"Dataset '{dataset}' does not exist in modelparams/")

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
        return f"https://nomads.ncep.noaa.gov/dods/gfswave/gfswave_global_{y}{m}{d}_{h}z"
    
    if dataset == "ecmwfatmos":
        return f"https://example.ecmwf.int/era5_{y}{m}{d}_{h}.nc"   # placeholder
    
    if dataset == "ecmwfwave":
        return f"https://example.ecmwf.int/era5_wave_{y}{m}{d}_{h}.nc"
    
    if dataset == "hycom":
        return f"https://hycom.org/dods/datasets/global_analysis_forecast/{y}{m}{d}.nc"
    
    if dataset == "cmems":
        return f"https://my.cmems-duacs.org/dods/global-analysis-forecast-phy/{y}{m}{d}.nc"

    raise ValueError("Unknown dataset source")
