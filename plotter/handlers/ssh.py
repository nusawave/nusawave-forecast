from ..core.base_handler import BaseHandler
import cartopy.crs as ccrs

class SshHandler(BaseHandler):
    def load(self, ds):
        return ds["ssh"]

    def plot(self, ax, ssh):
        cs = ax.contour(
            ssh.lon, ssh.lat, ssh,
            colors="red",
            linewidths=0.5,
            transform=ccrs.PlateCarree(),
        )
        return None
