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
from matplotlib.ticker import FuncFormatter
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

    def __format_tick__(self, x, pos):
        return f'{x:g}'

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

        if im is not None:
            fig.canvas.draw()
            bbox = ax.get_position()
            cbar_width = bbox.width-(bbox.width*0.3)
            cbar_left = bbox.x0 + (bbox.width*0.25)
            cbar_bottom = bbox.y0 - 0.025
            cbar_height = 0.02
            cbar_ax = fig.add_axes([cbar_left, cbar_bottom, cbar_width, cbar_height])

            cbar = fig.colorbar(im, 
                                cax=cbar_ax, 
                                ticks = self.config.levels,
                                orientation='horizontal', 
                                pad=0.05,
                                extend=self.config.extend)

            cbar.set_label("")
            cbar_ax.text(
                1.05, -1.1,
                f"{self.config.unit}",
                va="center",
                ha="left",
                fontsize=9,
                fontname="monospace",
                rotation=0,
                transform=cbar_ax.transAxes
            )

            cbar.ax.tick_params(labelsize=8)
            cbar.ax.xaxis.set_major_formatter(FuncFormatter(self.__format_tick__))

            if self.config.arrlabel is not None:
                cbar_bbox = ax.get_position()
                arrow_x = cbar_bbox.x0
                arrow_y = cbar_bbox.y0 - 0.04  # Center vertically with the colorbar

                fig.text(arrow_x+0.08, arrow_y, self.config.arrlabel, fontsize=8, ha='center', va='center')
                arrax = fig.add_axes([arrow_x,arrow_y-0.005,0.014,0.01], frameon=True)
                arrow_length = 0.015  # Length of the arrow
                arrow_width = 0.01  # Width of the arrow shaft
                head_width = 0.006  # Width of the arrow head
                head_length = 0.01  # Length of the arrow head

                arrax.arrow(0+0.02, 0, arrow_length, arrow_width, head_width=head_width, head_length=head_length, fc='k', ec='k')
                arrax.axis('off')

        ax.coastlines()
        apply_bbox(ax, self.config.bbox)

        varbox = TextArea(
            f"{self.config.var2display}\n{self.config.region}", 
            textprops=dict(
                color="k", 
                size=10,  
                # weight='bold',
                family='monospace'
            )
        )
        time_delta = (self.config.time_value - self.config.baserun).total_seconds()/3600
        initime = f'Initial: {self.config.baserun.strftime("%b %d, %Y - %HUTC")}'
        if self.config.time_value == self.config.baserun:
            fcstime = f'Analysis: {self.config.time_value.strftime("%b %d, %Y - %HUTC")} (t+000h)'
        else:
            fcstime = f'Forecast: {self.config.time_value.strftime("%b %d, %Y - %HUTC")} (t+{time_delta:03g}h)'
        timebox = TextArea(
            f"{initime}\n{fcstime}",
            textprops=dict(
                color="k", 
                size=8, 
                family='monospace',
                horizontalalignment='right'
            )
        )
        source = f'Source: {self.config.datasource}'
        credit = f'Nusawave Forecast \u00A9{datetime.now().year}'
        sourcetext = TextArea(
            f"{source}",
            textprops=dict(
                color="k", 
                size=7, 
                # weight='bold',
                family='monospace',
                horizontalalignment='left'
            )
        )
        credittext = TextArea(
            f"{credit}",
            textprops=dict(
                color="k", 
                size=10, 
                family='monospace',
                horizontalalignment='left',
                rotation=90
            )
        )
        logovarbox = HPacker(children=[varbox],
                    align="center",
                    pad=0, sep=2)
        timeinfobox = HPacker(children=[timebox],
                    align="center",
                    pad=0, sep=2)
        sourcebox = HPacker(children=[sourcetext],
                        align="center",
                        pad=0, sep=2)
        creditbox = HPacker(children=[credittext],
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
                                        child=sourcebox, pad=0.,
                                        frameon=False,
                                        bbox_to_anchor=(0., -0.01),
                                        bbox_transform=ax.transAxes,
                                        borderpad=0.1,)
        lsidebox = AnchoredOffsetbox(loc='lower left',
                                        child=creditbox, pad=0.,
                                        frameon=False,
                                        bbox_to_anchor=(1.005, 0),
                                        bbox_transform=ax.transAxes,
                                        borderpad=0.1,)        
        plt.tick_params(axis='both', which='major', labelsize=4)
        plt.tick_params(axis='both', which='major', labelsize=4)
        ax.add_artist(uleftbox)
        ax.add_artist(urightbox)
        ax.add_artist(lleftbox)
        ax.add_artist(lsidebox)

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
