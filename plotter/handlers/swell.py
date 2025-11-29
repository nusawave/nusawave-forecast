from ..core.base_handler import BaseHandler
import cartopy.crs as ccrs
import numpy as np

class SwellHandler(BaseHandler):
    def load(self, ds):
        return ds["swell_1"], ds["swdir_1"]

    def plot(self, ax, data):
        h, d = data

        im = ax.pcolormesh(
            h.lon, h.lat, h,
            cmap=self.config.cmap,
            shading="auto",
            transform=ccrs.PlateCarree(),
        )

        ax.quiver(
            h.lon, h.lat,
            -np.sin(np.deg2rad(d)),
            -np.cos(np.deg2rad(d)),
            transform=ccrs.PlateCarree(),
            scale=self.config.arrowscale,
        )

        return im
