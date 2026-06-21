"""Load GFS Wave data from NOMADS HTTPS GRIB2 (OpenDAP retired Feb 2026)."""

import tempfile
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

import cfgrib
import xarray as xr

NOMADS_GFSWAVE_BASE = (
    "https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod"
)
CACHE_DIR = Path(tempfile.gettempdir()) / "nusawave_grib_cache"


def gfswave_grib_url(cycle: str, forecast_hour: int) -> str:
    """Return HTTPS URL for a single GFS Wave 0.25° global GRIB2 file."""
    y, m, d, h = cycle[:4], cycle[4:6], cycle[6:8], cycle[8:10]
    fname = f"gfswave.t{h}z.global.0p25.f{forecast_hour:03d}.grib2"
    return f"{NOMADS_GFSWAVE_BASE}/gfs.{y}{m}{d}/{h}/wave/gridded/{fname}"


def pick_latest_gfswave_cycle() -> str:
    """Pick latest likely-available GFS synoptic cycle (00/06/12/18 UTC)."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    adjusted = now - timedelta(hours=5)
    hour = (adjusted.hour // 6) * 6
    cycle = adjusted.replace(hour=hour, minute=0, second=0, microsecond=0)
    return cycle.strftime("%Y%m%d%H")


def _download(url: str, cache_path: Path) -> Path:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    if not cache_path.exists():
        print(f"[INFO] Downloading {url}")
        urllib.request.urlretrieve(url, cache_path)
    return cache_path


def _normalize_coords(da: xr.DataArray) -> xr.DataArray:
    rename = {}
    if "longitude" in da.coords:
        rename["longitude"] = "lon"
    if "latitude" in da.coords:
        rename["latitude"] = "lat"
    if rename:
        da = da.rename(rename)
    return da


def _open_grib_file(path: Path) -> xr.Dataset:
    parts = cfgrib.open_datasets(str(path))
    merged = xr.merge(parts, compat="override")
    return merged


def normalize_gfswave_dataset(ds: xr.Dataset) -> xr.Dataset:
    """Map GRIB shortNames to legacy OpenDAP variable names used by handlers."""
    out = {}

    if "u" in ds:
        out["ugrdsfc"] = _normalize_coords(ds["u"])
    if "v" in ds:
        out["vgrdsfc"] = _normalize_coords(ds["v"])
    if "swh" in ds:
        out["htsgwsfc"] = _normalize_coords(ds["swh"])
    if "dirpw" in ds:
        out["dirpwsfc"] = _normalize_coords(ds["dirpw"])

    if "shts" in ds and "orderedSequenceData" in ds["shts"].dims:
        swell_mag = ds["shts"].isel(orderedSequenceData=0)
        out["swell_1"] = _normalize_coords(swell_mag)
    if "swdir" in ds and "orderedSequenceData" in ds["swdir"].dims:
        swell_dir = ds["swdir"].isel(orderedSequenceData=0)
        out["swdir_1"] = _normalize_coords(swell_dir)

    if not out:
        raise ValueError("No recognized GFS Wave variables in GRIB dataset")

    time_val = None
    if "valid_time" in ds.coords:
        time_val = ds["valid_time"]
    elif "time" in ds.coords and "step" in ds.coords:
        time_val = ds["time"] + ds["step"]
    elif "time" in ds.coords:
        time_val = ds["time"]

    result = xr.Dataset(out)
    if time_val is not None:
        result = result.assign_coords(time=time_val)
        for name in result.data_vars:
            result[name] = result[name].expand_dims("time")
    return result


def load_gfswave_forecast(cycle: str, forecast_hour: int, cache: bool = True) -> xr.Dataset:
    """Load one GFS Wave forecast hour as handler-compatible xarray Dataset."""
    url = gfswave_grib_url(cycle, forecast_hour)
    if cache:
        cache_path = CACHE_DIR / cycle / f"f{forecast_hour:03d}.grib2"
        path = _download(url, cache_path)
    else:
        tmp = tempfile.NamedTemporaryFile(suffix=".grib2", delete=False)
        urllib.request.urlretrieve(url, tmp.name)
        path = Path(tmp.name)

    raw = _open_grib_file(path)
    return normalize_gfswave_dataset(raw)


def load_gfswave_cycle(cycle: str, max_hours: int) -> xr.Dataset:
    """Load consecutive hourly forecasts into a single dataset with time dimension."""
    datasets = []
    for t in range(max_hours):
        try:
            ds = load_gfswave_forecast(cycle, t)
            datasets.append(ds)
        except Exception as exc:
            print(f"[WARN] Stopping at t+{t:03d}h: {exc}")
            break

    if not datasets:
        raise RuntimeError(f"No GFS Wave data loaded for cycle {cycle}")

    return xr.concat(datasets, dim="time")
