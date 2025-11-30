from ..core.base_handler import BaseHandler
from ..core.utils import load_model_params
import cartopy.crs as ccrs

class RainrateHandler(BaseHandler):
    def load(self, ds):
        mapper = load_model_params(self.config.dataset)
        varnames = mapper["rainrate"]
        dset = ds[varnames["var"]]
        dset = self.select_time(dset, self.config)
        dset = self.select_bbox(dset, self.config)
        dset = dset*3600
        return dset

    def plot(self, ax, rain):
        im = ax.pcolormesh(
            rain.lon, rain.lat, rain,
            cmap=self.config.cmap,
            shading="auto",
            vmin=self.config.clims[0],
            vmax=self.config.clims[1],
            transform=ccrs.PlateCarree(),
        )
        return im
