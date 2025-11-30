from ..core.base_handler import BaseHandler
from ..core.utils import load_model_params, select_time, select_depth, select_bbox
import cartopy.crs as ccrs

class SeacurrentHandler(BaseHandler):
    def load(self, ds):
        mapper = load_model_params(self.config.dataset)
        varnames = mapper["seacurrent"]
        u = ds[varnames["u"]]
        v = ds[varnames["v"]]
        u = self.select_time(u)
        v = self.select_time(v)
        u = self.select_depth(u)
        v = self.select_depth(v)
        u = self.select_bbox(u)
        v = self.select_bbox(v)
        return u, v

    def plot(self, ax, u, v):

        skip = self.config.quiver.get("skip", 5)
        ax.quiver(
            u.lon[::skip], u.lat[::skip],
            u[::skip, ::skip], v[::skip, ::skip],
            transform=ccrs.PlateCarree(),
            scale=self.config.quiver.scale,
            width=0.002,
        )
        return None
