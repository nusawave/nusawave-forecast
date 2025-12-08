from ..core.base_handler import BaseHandler
from ..core.utils import load_model_params, select_bbox, select_time, select_level, compute_quiver_params
import cartopy.crs as ccrs
import numpy as np
import matplotlib.colors as mcolors

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
        im, iq = None, None
        u, v = data
        lon = u.lon.values
        lat = u.lat.values
        u_np = u.values
        v_np = v.values
        mag = np.sqrt(u_np**2 + v_np**2)
        u_np = u_np / mag
        v_np = v_np / mag
        cmap = mcolors.ListedColormap(self.config.cmap)
        norm = mcolors.BoundaryNorm(
            boundaries=self.config.levels,
            ncolors=cmap.N,
            extend=self.config.extend,
        )
        skip, scale = compute_quiver_params(u.lat, u.lon, self.config)
        if self.config.quiver.get('skip') and self.config.quiver.get('scale') is not None:
            skip = self.config.quiver.get('skip')
            scale = self.config.quiver.get('scale')
        im = ax.contourf(
            u.lon, u.lat, mag,
            cmap=cmap,
            norm=norm,
            levels=self.config.levels,
            extend=self.config.extend,
            transform=ccrs.PlateCarree(),
        )
        iq = ax.quiver(
            lon[::skip], lat[::skip],
            u_np[::skip, ::skip], v_np[::skip, ::skip],
            transform=ccrs.PlateCarree(),
            scale=scale,
            width=self.config.quiver.get("width"),
            headwidth=self.config.quiver.get("headwidth"),
            headlength=self.config.quiver.get("headlength"),
            headaxislength=self.config.quiver.get("headaxislength"),
            minlength=self.config.quiver.get("minlength"),
            minshaft=self.config.quiver.get("minshaft"),
            pivot=self.config.quiver.get("pivot"),
        )
        return im, iq