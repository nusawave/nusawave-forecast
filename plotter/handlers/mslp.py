from ..core.base_handler import BaseHandler
import cartopy.crs as ccrs

class MslpHandler(BaseHandler):
    def load(self, ds):
        return ds["prmslmsl"]

    def plot(self, ax, mslp):
        cs = ax.contour(
            mslp.lon, mslp.lat, mslp / 100,  # hPa
            colors="black",
            linewidths=0.7,
            transform=ccrs.PlateCarree(),
        )
        ax.clabel(cs, fontsize=6)
        return None  # no colorbar
