import importlib
import os
import sys
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from .utils import get_projection, apply_bbox, deep_update
from .config_loader import load_param_config
from pathlib import Path
from matplotlib.offsetbox import (AnchoredOffsetbox, HPacker,
                                TextArea, OffsetImage)
from datetime import datetime

def _ensure_project_root():
    """
    Ensure the project root (containing the 'plotter' package)
    is available in sys.path, regardless of where the script is executed.
    """
    current_file = Path(__file__).resolve()

    root = current_file.parents[2]

    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

class Plotter:
    """Main engine to plot any parameter using plugin handlers."""

    def __init__(self, config):
        self.config = config
        self.yaml_cfg  = load_param_config()

    def _apply_param_config(self, param):
        settings = self.yaml_cfg.get("variables", {}).get(param, {})
        for key, value in settings.items():
            if hasattr(self.config, key) and isinstance(getattr(self.config, key), dict):
                deep_update(getattr(self.config, key), value)
            else:
                setattr(self.config, key, value)

    def _apply_region_config(self, region):
        settings = self.yaml_cfg.get("regions", {}).get(region, {})
        for key, value in settings.items():
            if hasattr(self.config, key) and isinstance(getattr(self.config, key), dict):
                deep_update(getattr(self.config, key), value)
            else:
                setattr(self.config, key, value)

    def _load_handler(self, param):
        
        _ensure_project_root()
        module_name = f"plotter.handlers.{param}"

        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(f"[ERROR] Handler '{module_name}' not found: {e}")

        class_name = param.capitalize() + "Handler"

        if not hasattr(module, class_name):
            raise ImportError(f"[ERROR] Class '{class_name}' not found in '{module_name}'")

        handler_class = getattr(module, class_name)
        return handler_class(self.config)

    def plot_map(self, ds, param):
        self._apply_region_config(self.config.region)
        self._apply_param_config(param)
        handler = self._load_handler(param)
        data = handler.load(ds)

        proj = get_projection(self.config.proj)
        fig = plt.figure(figsize=self.config.figsize, dpi=self.config.dpi)
        ax = plt.axes(projection=proj)

        im = handler.plot(ax, data)

        ax.coastlines()
        apply_bbox(ax, self.config.bbox)

        varbox = TextArea(
            f"MetOcean Forecast\n{self.config.var2display}\n{self.config.region}", 
            textprops=dict(
                color="k", 
                # size=3.5,  
                weight='bold',
                family='monospace'
            )
        )
        time_delta = (self.config.time_value - self.config.baserun).total_seconds()/3600
        initime = f'Initial: {self.config.baserun.strftime("%HUTC %Y-%m-%d")}'
        if self.config.time_value == self.config.baserun:
            fcstime = f'Analysis: {self.config.time_value.strftime("%HUTC %Y-%m-%d")} (t+0)'
        else:
            fcstime = f'Forecast: {self.config.time_value.strftime("%HUTC %Y-%m-%d")} (t+{time_delta:g})'
        timebox = TextArea(
            f"{initime}\n{fcstime}",
            textprops=dict(
                color="k", 
                size=9, 
                family='monospace',
                horizontalalignment='right'
            )
        )
        source = f'Source: {self.config.datasource}'
        credit = f'Created by Nusawave Forecast.\n           \u00A9{datetime.now().year}'
        sourcecredittext = TextArea(
            f"{source}\n{credit}",
            textprops=dict(
                color="k", 
                size=5.5, 
                # weight='bold',
                family='monospace',
                horizontalalignment='left'
            )
        )
        logovarbox = HPacker(children=[varbox],
                    align="center",
                    pad=0, sep=2)
        timeinfobox = HPacker(children=[timebox],
                    align="center",
                    pad=0, sep=2)
        sourcecreditbox = HPacker(children=[sourcecredittext],
                        align="center",
                        pad=0, sep=2)

        uleftbox = AnchoredOffsetbox(loc='lower left',
                                        child=logovarbox, pad=0.,
                                        frameon=False,
                                        bbox_to_anchor=(0, 1.),
                                        bbox_transform=ax.transAxes,
                                        borderpad=0.1,)
        urightbox = AnchoredOffsetbox(loc='lower right',
                                        child=timeinfobox, pad=0.,
                                        frameon=False,
                                        bbox_to_anchor=(1., 1.01),
                                        bbox_transform=ax.transAxes,
                                        borderpad=0.1,)
        lleftbox = AnchoredOffsetbox(loc='upper left',
                                        child=sourcecreditbox, pad=0.,
                                        frameon=False,
                                        bbox_to_anchor=(0., -0.06),
                                        bbox_transform=ax.transAxes,
                                        borderpad=0.1,)
        
        plt.tick_params(axis='both', which='major', labelsize=4)
        plt.tick_params(axis='both', which='major', labelsize=4)
        ax.add_artist(uleftbox)
        ax.add_artist(urightbox)
        ax.add_artist(lleftbox)

        if im is not None:
            plt.colorbar(im, ax=ax, shrink=0.7)

        if self.config.outfile:
            if not os.path.exists(os.path.dirname(self.config.outfile)):
                os.makedirs(os.path.dirname(self.config.outfile))
            plt.savefig(self.config.outfile, format="webp", dpi=self.config.dpi, bbox_inches='tight')

        plt.close(fig)

    def plot_route(self, ds, route_points):
        """Later: along-track interpolation."""
        raise NotImplementedError

    def plot_station(self, ds, lat, lon):
        """Later: time-series plotting."""
        raise NotImplementedError
