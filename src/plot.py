import argparse
import xarray as xr
from plotter.core.plotter import Plotter
from plotter.core.plot_config import PlotConfig
from plotter.core.config_loader import load_param_config
from plotter.core.utils import get_dataset_url

def parse_args():
    parser = argparse.ArgumentParser(description="NusaWave Plotting Engine")
    parser.add_argument("--dataset", required=True,
                        choices=["gfsatmos", "gfswave", "ecmwfatmos", "ecmwfwave", "hycom", "cmems"])
    parser.add_argument("--cycle", required=False, help="YYYYMMDDHH model cycle")
    parser.add_argument("--MAXFORECAST", type=int, default=3, help="Forecast length in days")
    parser.add_argument("--region", default="all", help="Region name or 'all'")

    return parser.parse_args()


def main():
    args = parse_args()

    # ----------------------------------------------------
    # 1. GET URL based on dataset + cycle
    # ----------------------------------------------------
    url = get_dataset_url(args.dataset, args.cycle)
    print(f"[INFO] Loading dataset: {url}")
    ds = xr.open_dataset(url)

    # Forecast time dimension
    max_t = args.MAXFORECAST * 24  # convert days → hours
    max_t = min(max_t, ds.dims["time"])

    # ----------------------------------------------------
    # 2. Load YAML config
    # ----------------------------------------------------
    yaml_cfg = load_param_config()
    yaml_defaults = yaml_cfg.get("defaults", {})
    yaml_params = yaml_cfg.get("variables", {})
    yaml_regions = yaml_cfg.get("regions", {})

    regions = [args.region] if args.region != "all" else list(yaml_regions.keys())

    # ----------------------------------------------------
    # 3. Loop: region → time → parameter
    # ----------------------------------------------------
    params = yaml_params.keys()

    for region in regions:
        for t in range(max_t):
            for param in params:

                cfg = PlotConfig(
                    dataset=args.dataset,
                    region=region,
                    time_index=t,
                    **yaml_defaults,
                    **yaml_params[param]
                )

                cfg.outfile = f"plots/{args.dataset}/{region}/{param}_{t:03d}.webp"

                plotter = Plotter(cfg)
                plotter.plot_map(ds, param)


if __name__ == "__main__":
    main()
