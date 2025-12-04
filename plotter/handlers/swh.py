from ..core.utils import load_model_params, select_bbox, select_time
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
        skip = self.config.quiver.get("skip", 5)
        scale = self.config.quiver.get("scale", 80)
        extend = self.config.extend

        im = ax.contourf(
            mag.lon, mag.lat, mag,
            cmap=cmap,
            norm=norm,
            levels=self.config.levels,
            shading="auto",
            extend=extend,
            transform=ccrs.PlateCarree(),
        )

        ax.quiver(
            lon[::skip], lat[::skip],
            u[::skip, ::skip], v[::skip, ::skip],
            transform=ccrs.PlateCarree(),
            scale=scale,
        )

        return im
