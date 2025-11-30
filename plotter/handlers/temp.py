from ..core.utils import load_model_params, select_bbox, select_time, select_level
from ..core.base_handler import BaseHandler
import cartopy.crs as ccrs

class TemperatureHandler(BaseHandler):
    def load(self, ds):
        mapper = load_model_params(self.config.dataset)
        varnames = mapper["temp"]
        dset = ds[varnames["var"]]
        dset = select_time(dset, self.config)
        dset = select_level(dset, self.config)
        dset = select_bbox(dset, self.config)
        return dset

    def plot(self, ax, tmp):
        return ax.pcolormesh(
            tmp.lon, tmp.lat, tmp,
            cmap=self.config.cmap,
            shading="auto",
            transform=ccrs.PlateCarree(),
        )
