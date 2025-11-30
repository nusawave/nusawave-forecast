from ..core.base_handler import BaseHandler
from ..selectors import load_selector
import cartopy.crs as ccrs

class WindHandler(BaseHandler):
    def load(self, ds):
        mapper = load_selector(self.config.dataset)
        varnames = mapper["wind"]

        u = ds[varnames["u"]]
        v = ds[varnames["v"]]

        u = self.select_time(u, self.config)
        u = self.select_level(u, self.config)
        u = self.select_bbox(u, self.config)
        v = self.select_time(v, self.config)
        v = self.select_level(v, self.config)
        v = self.select_bbox(v, self.config)

        return u, v

    def plot(self, ax, u, v):

        mag = (u**2 + v**2)**0.5
        skip = self.config.quiver.get("skip", 5)
        scale = self.config.quiver.get("scale", 80)
        
        ax.pcolormesh(
            mag.lon, mag.lat, mag,
            cmap=self.config.cmap,
            shading="auto",
            transform=ccrs.PlateCarree(),
        )
        
        ax.quiver(
            u.lon[::skip], u.lat[::skip],
            u[::skip, ::skip], v[::skip, ::skip],
            transform=ccrs.PlateCarree(),
            scale=scale,
            width=0.001,
        )
        return None
