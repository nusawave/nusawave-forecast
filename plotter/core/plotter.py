import importlib
import os
import sys
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from .utils import get_projection, apply_bbox, deep_update
from .config_loader import load_param_config
from pathlib import Path

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

        if im is not None:
            plt.colorbar(im, ax=ax, shrink=0.7)

        if self.config.outfile:
            if not os.path.exists(os.path.dirname(self.config.outfile)):
                os.makedirs(os.path.dirname(self.config.outfile))
            plt.savefig(self.config.outfile, format="webp", dpi=self.config.dpi)

        plt.close(fig)

    def plot_route(self, ds, route_points):
        """Later: along-track interpolation."""
        raise NotImplementedError

    def plot_station(self, ds, lat, lon):
        """Later: time-series plotting."""
        raise NotImplementedError
