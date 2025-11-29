from ..core.base_handler import BaseHandler
import cartopy.crs as ccrs
import numpy as np

class WavesHandler(BaseHandler):
    def load(self, ds):
        return ds["htsgwsfc"], ds["dirpwsfc"]

    def plot(self, ax, data):
        h, d = data
        
        # wave height shading
        im = ax.pcolormesh(
            h.lon, h.lat, h,
            cmap=self.config.cmap,
            shading="auto",
            transform=ccrs.PlateCarree(),
        )

        # wave direction arrows
        ax.quiver(
            h.lon, h.lat,
            -np.sin(np.deg2rad(d)),
            -np.cos(np.deg2rad(d)),
            transform=ccrs.PlateCarree(),
            scale=self.config.arrowscale,
        )

        return im
