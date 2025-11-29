from ..core.base_handler import BaseHandler
import cartopy.crs as ccrs

class HumidityHandler(BaseHandler):
    def load(self, ds):
        return ds["rhprs"]

    def plot(self, ax, rh):
        return ax.pcolormesh(
            rh.lon, rh.lat, rh,
            cmap=self.config.cmap,
            shading="auto",
            transform=ccrs.PlateCarree(),
        )
