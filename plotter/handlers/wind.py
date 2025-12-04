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
        width = self.config.quiver.get("width", 0.001)
        headwidth=self.config.quiver.get("headwidth",5.5)
        headlength=self.config.quiver.get("headlength", 6)
        headaxislength=self.config.quiver.get("headaxislength", 4)
        minlength=self.config.quiver.get("minlength", 1)
        minshaft=self.config.quiver.get("minshaft", 1)

        mag = np.sqrt(u_np**2 + v_np**2)
        u_np = u_np / mag
        v_np = v_np / mag

        im = ax.contourf(
            u.lon, u.lat, mag,
            cmap=self.config.cmap,
            shading="auto",
            extend='max',
            transform=ccrs.PlateCarree(),
        )

        ax.quiver(
            lon[::skip], lat[::skip],
            u_np[::skip, ::skip], v_np[::skip, ::skip],
            transform=ccrs.PlateCarree(),
            scale=scale,
            width=width,
            headwidth=headwidth,
            headlength=headlength,
            headaxislength=headaxislength,
            minlength=minlength,
            minshaft=minshaft,
        )

        return im