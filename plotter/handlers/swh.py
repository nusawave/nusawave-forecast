from ..core.utils import load_model_params, select_bbox, select_time, compute_quiver_params
from ..core.base_handler import BaseHandler
import cartopy.crs as ccrs
import numpy as np
import matplotlib.colors as mcolors

class SwhHandler(BaseHandler):
    def load(self, ds):
        mapper = load_model_params(self.config.dataset)
        varnames = mapper["swh"]
        mag = ds[varnames["mag"]]
        dir = ds[varnames["dir"]]
        mag = select_time(mag, self.config)
        dir = select_time(dir, self.config)
        mag = select_bbox(mag, self.config)
        dir = select_bbox(dir, self.config)
        return mag, dir

    def plot(self, ax, data):
        im, iq = None, None
        mag, direction = data

        lon = mag.lon.values
        lat = mag.lat.values

        dir_rad = np.deg2rad(direction.values)
        u = -np.sin(dir_rad)
        v = -np.cos(dir_rad)

        cmap = mcolors.ListedColormap(self.config.cmap)
        norm = mcolors.BoundaryNorm(
            boundaries=self.config.levels,
            ncolors=cmap.N,
            extend=self.config.extend,
        )
        skip, scale = compute_quiver_params(mag.lat, mag.lon, self.config)
        if self.config.quiver.get('skip') and self.config.quiver.get('scale') is not None:
            skip = self.config.quiver.get('skip')
            scale = self.config.quiver.get('scale')
        im = ax.contourf(
            mag.lon, mag.lat, mag,
            cmap=cmap,
            norm=norm,
            levels=self.config.levels,
            extend=self.config.extend,
            transform=ccrs.PlateCarree(),
        )
        iq = ax.quiver(
            lon[::skip], lat[::skip],
            u[::skip, ::skip], v[::skip, ::skip],
            transform=ccrs.PlateCarree(),
            scale=scale,
            width=self.config.quiver.get("width"),
            headwidth=self.config.quiver.get("headwidth"),
            headlength=self.config.quiver.get("headlength"),
            headaxislength=self.config.quiver.get("headaxislength"),
            minlength=self.config.quiver.get("minlength"),
            minshaft=self.config.quiver.get("minshaft"),
            pivot=self.config.quiver.get("pivot"),
        )
        return im, iq
