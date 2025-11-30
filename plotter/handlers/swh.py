from ..core.utils import load_model_params, select_bbox, select_time
from ..core.base_handler import BaseHandler
import cartopy.crs as ccrs
import numpy as np

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

        skip = self.config.quiver.get("skip", 5)
        scale = self.config.quiver.get("scale", 80)

        im = ax.pcolormesh(
            mag.lon, mag.lat, mag,
            cmap=self.config.cmap,
            shading="auto",
            transform=ccrs.PlateCarree(),
        )

        ax.quiver(
            lon[::skip], lat[::skip],
            u[::skip, ::skip], v[::skip, ::skip],
            transform=ccrs.PlateCarree(),
            scale=scale,
        )

        return im
