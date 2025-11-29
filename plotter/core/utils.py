import cartopy.crs as ccrs

def get_projection(name):
    if name == "mercator":
        return ccrs.Mercator()
    elif name == "plate":
        return ccrs.PlateCarree()
    elif name == "northpolar":
        return ccrs.NorthPolarStereo()
    return ccrs.PlateCarree()

def apply_bbox(ax, bbox):
    if bbox:
        min_lon, max_lon, min_lat, max_lat = bbox
        ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())
