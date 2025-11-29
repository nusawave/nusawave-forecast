from ..core.base_handler import BaseHandler
import cartopy.crs as ccrs

class SstHandler(BaseHandler):
    def load(self, ds):
        return ds["sst"]

    def plot(self, ax, sst):
        return ax.pcolormesh(
            sst.lon, sst.lat, sst,
            cmap=self.config.cmap,
            shading="auto",
            transform=ccrs.PlateCarree(),
        )
