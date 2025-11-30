from ..core.utils import load_model_params, select_bbox, select_time
from ..core.base_handler import BaseHandler
import cartopy.crs as ccrs
import numpy as np

class WavesHandler(BaseHandler):
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

    def plot(self, ax, mag, dir):
        
        skip = self.config.quiver.get("skip", 5)

        # wave height shading
        im = ax.pcolormesh(
            mag.lon, mag.lat, mag,
            cmap=self.config.cmap,
            shading="auto",
            transform=ccrs.PlateCarree(),
        )

        # wave direction arrows
        ax.quiver(
            mag.lon[::skip], mag.lat[::skip],
            -np.sin(np.deg2rad(dir[::skip, ::skip])),
            -np.cos(np.deg2rad(dir[::skip, ::skip])),
            transform=ccrs.PlateCarree(),
            scale=self.config.quiver.scale,
        )

        return im
