import importlib
import os
import sys
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from .utils import get_projection, deep_update
from .config_loader import load_param_config
from pathlib import Path
from matplotlib.offsetbox import (AnchoredOffsetbox, HPacker,
                                TextArea)
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

    def _apply_bbox(self, ax, bbox):
        if bbox:
            min_lon, max_lon, min_lat, max_lat = bbox
            ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())
        
    def plot_map(self, ds, param):
        self._apply_region_config(self.config.region)
        self._apply_param_config(param)
        handler = self._load_handler(param)
        data = handler.load(ds)

        proj = get_projection(self.config.proj)
        fig = plt.figure(figsize=self.config.figsize, dpi=self.config.dpi)
        ax = plt.axes(projection=proj)

        im, iq = handler.plot(ax, data)
        print(im, iq)

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
            cbar.ax.tick_params(direction='inout', labelsize=8)
            cbar.ax.xaxis.set_major_formatter(FuncFormatter(self.__format_tick__))
            cbar.set_label("")
            cbar_ax.text(
                1.05, -0.8,
                f"{self.config.unit}",
                va="center",
                ha="left",
                fontsize=9,
                fontname="monospace",
                rotation=0,
                transform=cbar_ax.transAxes
            )

            if iq is not None:
                cbar_bbox = ax.get_position()
                arrow_x = cbar_bbox.x0
                arrow_y = cbar_bbox.y0 - 0.04  # Center vertically with the colorbar

                fig.text(arrow_x+0.08, arrow_y, self.config.arrlabel, fontsize=8, ha='center', va='center')
                arrax = fig.add_axes([arrow_x,arrow_y-0.005,0.014,0.01], frameon=True)
                arrow_length = 0.01  # Length of the arrow
                arrow_width = 0.01  # Width of the arrow shaft
                head_width = 0.01  # Width of the arrow head
                head_length = 0.01  # Length of the arrow head
                overhang = 1

                arrax.arrow(0+0.02, 0, arrow_length, arrow_width, head_width=head_width, head_length=head_length, overhang=overhang, fc='k', ec='k')
                arrax.axis('off')

        ax.coastlines(linewidth=1, zorder=2)
        ax.add_feature(cfeature.BORDERS, linewidth=1, zorder=3)
        ax.add_feature(cfeature.LAND, edgecolor='black', facecolor='gray', zorder=2)
        self._apply_bbox(ax, self.config.bbox)
        ax.spines['geo'].set_visible(True)
        gl = ax.gridlines(
            crs=ccrs.PlateCarree(),
            draw_labels=False,
            linewidth=0.3,
            color='w',
            linestyle='--'
        )

        # let cartopy choose tick positions
        xs = gl.xlocator.tick_values(*ax.get_extent(ccrs.PlateCarree())[:2])
        ys = gl.ylocator.tick_values(*ax.get_extent(ccrs.PlateCarree())[2:])
        
        # plot labels with background
        for x in xs[1:-1]:
            ax.text(
                x, self.config.bbox[2] + 0.3,
                LONGITUDE_FORMATTER(x),
                transform=ccrs.PlateCarree(),
                ha='center', va='bottom',
                fontsize=5, color='black',
                bbox=dict(fc='lightgrey', alpha=0.8, ec='none', boxstyle="round,pad=0.4")
            )
        
        for y in ys[1:-1]:
            ax.text(
                self.config.bbox[0] + 0.3, y,
                LATITUDE_FORMATTER(y),
                transform=ccrs.PlateCarree(),
                ha='left', va='center',
                fontsize=5, color='black',
                bbox=dict(fc='lightgrey', alpha=0.8, ec='none', boxstyle="round,pad=0.4")
            )

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
                size=6, 
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
            fname = f"{self.config.outfile}.{self.config.fileformat}"
            if not os.path.exists(os.path.dirname(self.config.outfile)):
                os.makedirs(os.path.dirname(self.config.outfile))
            plt.savefig(fname, format=self.config.fileformat, dpi=self.config.dpi, bbox_inches='tight')
            print(f"[INFO] File saved at {fname}")

        plt.close(fig)

    def plot_route(self, ds, route_points):
        """Later: along-track interpolation."""
        raise NotImplementedError

    def plot_station(self, ds, lat, lon):
        """Later: time-series plotting."""
        raise NotImplementedError
