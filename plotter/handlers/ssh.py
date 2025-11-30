from ..core.utils import load_model_params, select_bbox, select_time
from ..core.base_handler import BaseHandler
import cartopy.crs as ccrs

class SshHandler(BaseHandler):
    def load(self, ds):
        mapper = load_model_params(self.config.dataset)
        varnames = mapper["ssh"]
        dset = ds[varnames["var"]]
        dset = select_time(dset, self.config)
        dset = select_bbox(dset, self.config)
        return dset

    def plot(self, ax, ssh):
        cs = ax.contour(
            ssh.lon, ssh.lat, ssh,
            colors="red",
            linewidths=0.5,
            transform=ccrs.PlateCarree(),
        )
        return None
