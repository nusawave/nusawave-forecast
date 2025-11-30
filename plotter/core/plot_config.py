class PlotConfig:
    """
    Flexible config container.
    Explicit args for stability.
    **kwargs for future extensions or YAML overrides.
    """

    def __init__(
        self,
        # Styling and figure behavior
        proj="mercator",
        figsize=(8, 6),
        dpi=80,
        cmap="viridis",
        clims=None,
        outfile=None,

        # Scientific dimension selections
        time_index=None,      # time index (int)
        time_value=None,      # actual timestamp
        bbox=None,            # [min_lon, max_lon, min_lat, max_lat]
        level=None,           # pressure level (hPa)
        depth=None,           # depth selection (meters)
        dataset=None,         # gfs, ecmwf, hycom

        # Region name ("indonesia", "sumatra")
        region=None,

        **kwargs,
    ):
        # Explicit stable API
        self.proj = proj
        self.figsize = figsize
        self.dpi = dpi
        self.cmap = cmap
        self.clims = clims
        self.bbox = bbox
        self.outfile = outfile

        # Flexible scientific configuration
        self.time_index = time_index
        self.time_value = time_value
        self.level = level
        self.depth = depth
        self.dataset = dataset
        self.region = region

        self.quiver = {
            "skip": 5,
            "scale": 80,
            "width": 0.002,
            "color": "black",
        }

        self.contour = {
            "interval": 2,
            "linewidth": 0.7,
            "colors": "black",
        }

        # Dynamic config overrides (from YAML)
        for k, v in kwargs.items():
            setattr(self, k, v)