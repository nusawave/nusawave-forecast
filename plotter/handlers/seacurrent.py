from ..core.base_handler import BaseHandler
import cartopy.crs as ccrs

class CurrentsHandler(BaseHandler):
    def load(self, ds):
        return ds["uocn"], ds["vocn"]

    def plot(self, ax, data):
        u, v = data

        ax.quiver(
            u.lon, u.lat, u, v,
            transform=ccrs.PlateCarree(),
            scale=self.config.arrowscale,
            width=0.002,
        )
        return None
