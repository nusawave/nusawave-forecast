from ..core.base_handler import BaseHandler
from ..core.utils import load_model_params
import cartopy.crs as ccrs

class SstHandler(BaseHandler):
    def load(self, ds):
        mapper = load_model_params(self.config.dataset)
        varnames = mapper["seatemp"]
        return ds[varnames["var"]]

    def plot(self, ax, sst):
        return ax.pcolormesh(
            sst.lon, sst.lat, sst,
            cmap=self.config.cmap,
            shading="auto",
            transform=ccrs.PlateCarree(),
        )
