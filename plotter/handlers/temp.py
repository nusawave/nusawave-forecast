from ..core.base_handler import BaseHandler
import cartopy.crs as ccrs

class TemperatureHandler(BaseHandler):
    def load(self, ds):
        return ds["tmpsfc"]

    def plot(self, ax, tmp):
        return ax.pcolormesh(
            tmp.lon, tmp.lat, tmp,
            cmap=self.config.cmap,
            shading="auto",
            transform=ccrs.PlateCarree(),
        )
