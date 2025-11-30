from ..core.base_handler import BaseHandler
from ..core.utils import load_model_params, select_time, select_depth, select_bbox
import cartopy.crs as ccrs

class SeasaltHandler(BaseHandler):
    def load(self, ds):
        mapper = load_model_params(self.config.dataset)
        varnames = mapper["seasalt"]
        dset = ds[varnames["var"]]
        dset = select_time(dset, self.config)
        dset = select_depth(dset, self.config)
        dset = select_bbox(dset, self.config)
        return dset

    def plot(self, ax, sss):
        return ax.pcolormesh(
            sss.lon, sss.lat, sss,
            cmap=self.config.cmap,
            shading="auto",
            transform=ccrs.PlateCarree(),
        )
