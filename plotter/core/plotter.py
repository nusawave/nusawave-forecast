import importlib
import math
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
import pandas as pd

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

    def _region_label(self):
        region = self.config.region or ""
        return region.replace("_", " ").title()

    def _forecast_hour(self):
        if self.config.forecast_hour is not None:
            return int(self.config.forecast_hour)
        if self.config.baserun is not None and self.config.time_value is not None:
            delta = (
                pd.Timestamp(self.config.time_value) - pd.Timestamp(self.config.baserun)
            ).total_seconds() / 3600
            return int(round(delta))
        return 0

    def _valid_time(self):
        if self.config.baserun is not None and self.config.forecast_hour is not None:
            return pd.Timestamp(self.config.baserun) + pd.Timedelta(hours=self.config.forecast_hour)
        if self.config.time_value is not None:
            return pd.Timestamp(self.config.time_value)
        return pd.Timestamp(self.config.baserun)

    def _time_annotation_lines(self):
        baserun = pd.Timestamp(self.config.baserun)
        valid = self._valid_time()
        fh = self._forecast_hour()
        initime = f"Initial: {baserun.strftime('%b %d, %Y - %HUTC')}"
        if fh == 0:
            valid_line = f"Analysis: {valid.strftime('%b %d, %Y - %HUTC')} (t+000h)"
        else:
            valid_line = f"Forecast: {valid.strftime('%b %d, %Y - %HUTC')} (t+{fh:03d}h)"
        return initime, valid_line

    def _resolve_figsize(self):
        """Pick figure size from region bbox; portrait regions get a taller canvas."""
        bbox = self.config.bbox or [90, 150, -20, 25]
        lon_span = bbox[1] - bbox[0]
        lat_span = bbox[3] - bbox[2]
        lat_mid = (bbox[2] + bbox[3]) / 2
        map_w = max(lon_span * math.cos(math.radians(lat_mid)), 1e-6)
        map_h = max(lat_span, 1e-6)
        aspect = map_h / map_w
        portrait = aspect > 1.05
        if portrait:
            height = min(10.0, max(6.5, 6.5 * aspect))
            return (5.5, height), True
        width = min(11.0, max(7.0, 7.5 * (map_w / map_h)))
        return (width, 6.0), False

    def _add_map_annotations(self, ax, fig, portrait):
        initime, fcstime = self._time_annotation_lines()
        title_size = 7 if portrait else 9
        meta_size = 6 if portrait else 7

        if portrait:
            headertext = TextArea(
                f"{self.config.var2display}\n{self._region_label()}\n{initime}\n{fcstime}",
                textprops=dict(
                    color="k",
                    size=meta_size,
                    family="monospace",
                    linespacing=1.1,
                ),
            )
            headerbox = AnchoredOffsetbox(
                loc="upper left",
                child=HPacker(children=[headertext], align="center", pad=0, sep=2),
                pad=0.0,
                frameon=True,
                bbox_to_anchor=(0.0, 1.0),
                bbox_transform=ax.transAxes,
                borderpad=0.3,
            )
            headerbox.patch.set_facecolor("white")
            headerbox.patch.set_alpha(0.88)
            headerbox.patch.set_edgecolor("none")
            ax.add_artist(headerbox)
        else:
            varbox = TextArea(
                f"{self.config.var2display}\n{self._region_label()}",
                textprops=dict(color="k", size=title_size, family="monospace", linespacing=1.15),
            )
            timebox = TextArea(
                f"{initime}\n{fcstime}",
                textprops=dict(
                    color="k",
                    size=meta_size,
                    family="monospace",
                    horizontalalignment="right",
                    linespacing=1.15,
                ),
            )
            for box, loc, anchor in (
                (HPacker(children=[varbox], align="center", pad=0, sep=2), "upper left", (0.0, 1.0)),
                (HPacker(children=[timebox], align="center", pad=0, sep=2), "upper right", (1.0, 1.0)),
            ):
                artist = AnchoredOffsetbox(
                    loc=loc,
                    child=box,
                    pad=0.0,
                    frameon=True,
                    bbox_to_anchor=anchor,
                    bbox_transform=ax.transAxes,
                    borderpad=0.35,
                )
                artist.patch.set_facecolor("white")
                artist.patch.set_alpha(0.88)
                artist.patch.set_edgecolor("none")
                ax.add_artist(artist)

        source = f"Source: {self.config.datasource}"
        credit = f"Nusawave Forecast \u00A9{datetime.now().year}"
        sourcetext = TextArea(
            source,
            textprops=dict(color="k", size=6, family="monospace", horizontalalignment="left"),
        )
        sourcebox = AnchoredOffsetbox(
            loc="lower left",
            child=HPacker(children=[sourcetext], align="center", pad=0, sep=2),
            pad=0.0,
            frameon=False,
            bbox_to_anchor=(0.0, 0.0),
            bbox_transform=ax.transAxes,
            borderpad=0.2,
        )
        ax.add_artist(sourcebox)

        if portrait:
            credittext = TextArea(
                credit,
                textprops=dict(color="k", size=7, family="monospace", horizontalalignment="right"),
            )
            creditbox = AnchoredOffsetbox(
                loc="lower right",
                child=HPacker(children=[credittext], align="center", pad=0, sep=2),
                pad=0.0,
                frameon=False,
                bbox_to_anchor=(1.0, 0.0),
                bbox_transform=ax.transAxes,
                borderpad=0.2,
            )
            ax.add_artist(creditbox)
        else:
            credittext = TextArea(
                credit,
                textprops=dict(
                    color="k",
                    size=9,
                    family="monospace",
                    horizontalalignment="left",
                    rotation=90,
                ),
            )
            creditbox = AnchoredOffsetbox(
                loc="lower left",
                child=HPacker(children=[credittext], align="center", pad=0, sep=2),
                pad=0.0,
                frameon=False,
                bbox_to_anchor=(1.0, 0.0),
                bbox_transform=ax.transAxes,
                borderpad=0.1,
            )
            ax.add_artist(creditbox)

    def _apply_bbox(self, ax, bbox):
        if bbox:
            min_lon, max_lon, min_lat, max_lat = bbox
            ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())
        
    def plot_map(self, ds, param):
        self._apply_region_config(self.config.region)
        self._apply_param_config(param)
        handler = self._load_handler(param)
        data = handler.load(ds)

        figsize, portrait = self._resolve_figsize()
        self.config.figsize = figsize

        proj = get_projection(self.config.proj)
        fig = plt.figure(figsize=figsize, dpi=self.config.dpi)
        if portrait:
            fig.subplots_adjust(left=0.12, right=0.88, top=0.94, bottom=0.20)
        else:
            fig.subplots_adjust(left=0.06, right=0.94, top=0.92, bottom=0.14)
        ax = plt.axes(projection=proj)

        im, iq = handler.plot(ax, data)

        if im is not None:
            fig.canvas.draw()
            bbox = ax.get_position()
            cbar_width = bbox.width * 0.65
            cbar_left = bbox.x0 + (bbox.width - cbar_width) / 2
            cbar_bottom = bbox.y0 - (0.055 if portrait else 0.03)
            cbar_height = 0.018
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
                arrow_y = cbar_bbox.y0 - (0.055 if portrait else 0.04)

                fig.text(arrow_x + 0.06, arrow_y, self.config.arrlabel, fontsize=7, ha='center', va='center')
                arrax = fig.add_axes([arrow_x, arrow_y - 0.005, 0.014, 0.01], frameon=True)
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
        
        extent = ax.get_extent(ccrs.PlateCarree())
        lon_min, lon_max, lat_min, lat_max = extent

        # grid labels — fewer on portrait maps to reduce clutter
        label_step = 2 if portrait else 1
        for i, x in enumerate(xs[1:-1]):
            if i % label_step:
                continue
            ax.text(
                x, lat_min + (lat_max - lat_min) * 0.02,
                LONGITUDE_FORMATTER(x),
                transform=ccrs.PlateCarree(),
                ha='center', va='bottom',
                fontsize=5, color='black',
                bbox=dict(fc='lightgrey', alpha=0.8, ec='none', boxstyle="round,pad=0.4")
            )

        lat_label_x = lon_min + (lon_max - lon_min) * (0.02 if portrait else 0.01)
        for i, y in enumerate(ys[1:-1]):
            if i % label_step:
                continue
            ax.text(
                lat_label_x, y,
                LATITUDE_FORMATTER(y),
                transform=ccrs.PlateCarree(),
                ha='left', va='center',
                fontsize=5, color='black',
                bbox=dict(fc='lightgrey', alpha=0.8, ec='none', boxstyle="round,pad=0.4")
            )

        self._add_map_annotations(ax, fig, portrait)
        plt.tick_params(axis='both', which='major', labelsize=4)

        if self.config.outfile:
            fname = f"{self.config.outfile}.{self.config.fileformat}"
            if not os.path.exists(os.path.dirname(self.config.outfile)):
                os.makedirs(os.path.dirname(self.config.outfile))
            plt.savefig(fname, format=self.config.fileformat, dpi=self.config.dpi, bbox_inches=None, pad_inches=0.05)
            print(f"[INFO] File saved at {fname}")

        plt.close(fig)

    def plot_route(self, ds, route_points):
        """Later: along-track interpolation."""
        raise NotImplementedError

    def plot_station(self, ds, lat, lon):
        """Later: time-series plotting."""
        raise NotImplementedError
