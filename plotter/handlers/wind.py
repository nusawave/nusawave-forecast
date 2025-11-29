from ..core.base_handler import BaseHandler
import cartopy.crs as ccrs

class WindHandler(BaseHandler):
    def load(self, ds):
        return ds["ugrdsfc"], ds["vgrdsfc"]

    def plot(self, ax, data):
        u, v = data
        ax.quiver(
            u.lon, u.lat, u, v,
            transform=ccrs.PlateCarree(),
            scale=self.config.arrowscale,
            width=0.001,
        )
        return None
