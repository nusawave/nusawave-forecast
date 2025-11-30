from ..core.base_handler import BaseHandler
from ..core.utils import load_model_params, select_time, select_level, select_bbox
import cartopy.crs as ccrs

class HumidityHandler(BaseHandler):
    def load(self, ds):
        mapper = load_model_params(self.config.dataset)
        varnames = mapper["rh"]
        dset = ds[varnames["var"]]
        dset = self.select_time(dset)
        dset = self.select_level(dset)
        dset = self.select_bbox(dset)
        return dset
    
    def plot(self, ax, rh):
        return ax.pcolormesh(
            rh.lon, rh.lat, rh,
            cmap=self.config.cmap,
            shading="auto",
            transform=ccrs.PlateCarree(),
        )
