from ..core.base_handler import BaseHandler
import cartopy.crs as ccrs

class SssHandler(BaseHandler):
    def load(self, ds):
        return ds["sss"]

    def plot(self, ax, sss):
        return ax.pcolormesh(
            sss.lon, sss.lat, sss,
            cmap=self.config.cmap,
            shading="auto",
            transform=ccrs.PlateCarree(),
        )
