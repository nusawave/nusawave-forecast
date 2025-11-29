import importlib
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from .utils import get_projection, apply_bbox
from .config_loader import load_param_config

class Plotter:
    """Main engine to plot any parameter using plugin handlers."""

    def __init__(self, config):
        self.config = config
        self.param_config = load_param_config()

    def _apply_param_config(self, param):
        if param not in self.param_config:
            return

        overrides = self.param_config[param]
        for key, value in overrides.items():
            setattr(self.config, key, value)
            
    def _load_handler(self, param):
        module = importlib.import_module(f"nusawave_plotter.handlers.{param}")
        class_name = param.capitalize() + "Handler"
        handler_class = getattr(module, class_name)
        return handler_class(self.config)

    def plot_map(self, ds, param):
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
            plt.savefig(self.config.outfile, format="webp", dpi=self.config.dpi)

        plt.close(fig)

    def plot_route(self, ds, route_points):
        """Later: along-track interpolation."""
        raise NotImplementedError

    def plot_station(self, ds, lat, lon):
        """Later: time-series plotting."""
        raise NotImplementedError
