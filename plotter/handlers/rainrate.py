from ..core.base_handler import BaseHandler
import cartopy.crs as ccrs

class RainHandler(BaseHandler):
    def load(self, ds):
        return ds["apcpsfc"]

    def plot(self, ax, rain):
        im = ax.pcolormesh(
            rain.lon, rain.lat, rain,
            cmap=self.config.cmap,
            shading="auto",
            vmin=self.config.clims[0] if self.config.clims else None,
            vmax=self.config.clims[1] if self.config.clims else None,
            transform=ccrs.PlateCarree(),
        )
        return im
