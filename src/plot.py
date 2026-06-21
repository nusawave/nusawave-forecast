import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

# Non-interactive backend for headless/CI runs
os.environ.setdefault("MPLBACKEND", "Agg")

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from plotter.core.plotter import Plotter
from plotter.core.plot_config import PlotConfig
from plotter.core.config_loader import load_param_config
from plotter.core.utils import get_dataset_url, load_model_params

GFSWAVE_PARAMS = ("wind", "swh", "swell")
GFSATMOS_PARAMS = ("rainrate", "temp", "relhum", "mslp")
DATASET_PARAMS = {
    "gfswave": GFSWAVE_PARAMS,
    "gfsatmos": GFSATMOS_PARAMS,
}


def parse_args():
    parser = argparse.ArgumentParser(description="NusaWave Plotting Engine")
    parser.add_argument(
        "--dataset",
        required=True,
        choices=["gfsatmos", "gfswave", "ecmwfatmos", "ecmwfwave", "hycom", "cmems"],
    )
    parser.add_argument("--cycle", required=True, help="YYYYMMDDHH model cycle")
    parser.add_argument(
        "--max-hours",
        type=int,
        default=4,
        help="Forecast length in hours (default: 4)",
    )
    parser.add_argument(
        "--MAXFORECAST",
        type=int,
        default=None,
        help="Legacy: forecast length in days (overrides --max-hours if set)",
    )
    parser.add_argument("--region", default="all", help="Region name or 'all'")
    return parser.parse_args()


def params_for_dataset(dataset):
    if dataset in DATASET_PARAMS:
        return DATASET_PARAMS[dataset]
    mapper = load_model_params(dataset)
    skip = {"time", "lon", "lat", "source"}
    return [p for p in mapper.keys() if p not in skip]


def main():
    args = parse_args()
    baserun = datetime.strptime(args.cycle, "%Y%m%d%H")

    url = get_dataset_url(args.dataset, args.cycle)
    print(f"[INFO] Loading dataset: {url}")

    max_t = args.MAXFORECAST * 24 if args.MAXFORECAST is not None else args.max_hours

    yaml_cfg = load_param_config()
    yaml_defaults = yaml_cfg.get("defaults", {})
    yaml_params = yaml_cfg.get("variables", {})
    yaml_regions = yaml_cfg.get("regions", {})

    regions = [args.region] if args.region != "all" else list(yaml_regions.keys())
    params = params_for_dataset(args.dataset)
    params_load = load_model_params(args.dataset)

    maps_root = ROOT / "assets" / "maps" / args.dataset

    if args.dataset == "gfswave":
        from plotter.core.grib_loader import load_gfswave_forecast

        for t in range(max_t):
            try:
                ds = load_gfswave_forecast(args.cycle, t)
            except Exception as exc:
                print(f"[WARN] No data at t+{t:03d}h, stopping: {exc}")
                break

            tforecast = pd.Timestamp(ds["time"].values[0])

            for region in regions:
                for param in params:
                    if param not in yaml_params:
                        continue

                    print(f"[INFO] Plotting {param} for region {region} at t+{t:03d}h")

                    cfg = PlotConfig(
                        dataset=args.dataset,
                        region=region,
                        time_index=None,
                        time_value=pd.Timestamp(tforecast),
                        forecast_hour=t,
                        **yaml_defaults,
                        **yaml_params[param],
                    )

                    cfg.outfile = str(maps_root / region / f"{param}_{t:03d}")
                    cfg.baserun = baserun
                    cfg.datasource = params_load.get("source", args.dataset)

                    plotter = Plotter(cfg)
                    plotter.plot_map(ds, param)
        return

    import xarray as xr
    ds = xr.open_dataset(url, engine="netcdf4")
    max_t = min(max_t, ds.dims["time"])
    time_dim = params_load.get("time", "time")

    for region in regions:
        for t in range(max_t):
            tforecast = pd.to_datetime(ds.isel({time_dim: t})["time"].values)
            for param in params:
                if param not in yaml_params:
                    continue

                print(f"[INFO] Plotting {param} for region {region} at t+{t:03d}h")

                cfg = PlotConfig(
                    dataset=args.dataset,
                    region=region,
                    time_index=t,
                    time_value=tforecast,
                    forecast_hour=t,
                    **yaml_defaults,
                    **yaml_params[param],
                )

                cfg.outfile = str(maps_root / region / f"{param}_{t:03d}")
                cfg.baserun = baserun
                cfg.datasource = params_load.get("source", args.dataset)

                plotter = Plotter(cfg)
                plotter.plot_map(ds, param)


if __name__ == "__main__":
    main()
