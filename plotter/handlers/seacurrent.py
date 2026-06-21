from ..core.base_handler import BaseHandler
from ..core.utils import load_model_params, select_time, select_depth, select_bbox
import cartopy.crs as ccrs

class SeacurrentHandler(BaseHandler):
    def load(self, ds):
        mapper = load_model_params(self.config.dataset)
        varnames = mapper["seacurrent"]
        u = ds[varnames["u"]]
        v = ds[varnames["v"]]
        u = select_time(u, self.config)
        v = select_time(v, self.config)
        u = select_depth(u, self.config)
        v = select_depth(v, self.config)
        u = select_bbox(u, self.config)
        v = select_bbox(v, self.config)
        return u, v

    def plot(self, ax, data):
        u, v = data
        skip = self.config.quiver.get("skip", 5)
        scale = self.config.quiver.get("scale", 80)
        ax.quiver(
            u.lon[::skip], u.lat[::skip],
            u[::skip, ::skip], v[::skip, ::skip],
            transform=ccrs.PlateCarree(),
            scale=scale,
            width=0.002,
        )
        return None
