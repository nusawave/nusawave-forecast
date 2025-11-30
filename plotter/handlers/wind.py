from ..core.base_handler import BaseHandler
from ..core.utils import load_model_params, select_bbox, select_time, select_level
import cartopy.crs as ccrs
import numpy as np

class WindHandler(BaseHandler):
    def load(self, ds):
        mapper = load_model_params(self.config.dataset)
        varnames = mapper["wind"]

        u = ds[varnames["u"]]
        v = ds[varnames["v"]]

        u = select_time(u, self.config)
        u = select_level(u, self.config)
        u = select_bbox(u, self.config)
        v = select_time(v, self.config)
        v = select_level(v, self.config)
        v = select_bbox(v, self.config)

        return u, v

    def plot(self, ax, data):
        u, v = data

        lon = u.lon.values
        lat = u.lat.values
        u_np = u.values
        v_np = v.values

        skip = self.config.quiver.get("skip", 5)
        scale = self.config.quiver.get("scale", 80)

        mag = np.sqrt(u_np**2 + v_np**2)

        ax.pcolormesh(
            u.lon, u.lat, mag,
            cmap=self.config.cmap,
            shading="auto",
            transform=ccrs.PlateCarree(),
        )

        ax.quiver(
            lon[::skip], lat[::skip],
            u_np[::skip, ::skip], v_np[::skip, ::skip],
            transform=ccrs.PlateCarree(),
            scale=scale,
            width=0.001,
        )

        return None