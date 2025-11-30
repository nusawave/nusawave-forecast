from ..core.base_handler import BaseHandler
from ..core.utils import load_model_params, select_bbox, select_time, select_depth
import cartopy.crs as ccrs

class SstHandler(BaseHandler):
    def load(self, ds):
        mapper = load_model_params(self.config.dataset)
        varnames = mapper["seatemp"]
        dset = ds[varnames["var"]]
        dset = select_time(dset, self.config)
        dset = select_depth(dset, self.config)
        dset = select_bbox(dset, self.config)
        return dset

    def plot(self, ax, sst):
        return ax.pcolormesh(
            sst.lon, sst.lat, sst,
            cmap=self.config.cmap,
            shading="auto",
            transform=ccrs.PlateCarree(),
        )
