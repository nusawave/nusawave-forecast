class PlotConfig:
    """
    Flexible config container.
    Explicit args for stability.
    **kwargs for future extensions or YAML overrides.
    """

    def __init__(
        self,
        proj="mercator",
        figsize=(8, 6),
        dpi=120,
        cmap="viridis",
        clims=None,
        bbox=None,
        outfile=None,
        arrowscale=80,

        # new optional flexible parameters
        level=None,
        depth=None,
        dataset=None,

        **kwargs,
    ):
        # explicit stable API
        self.proj = proj
        self.figsize = figsize
        self.dpi = dpi
        self.cmap = cmap
        self.clims = clims
        self.bbox = bbox
        self.outfile = outfile
        self.arrowscale = arrowscale

        # flexible scientific extensions
        self.level = level
        self.depth = depth
        self.dataset = dataset

        # dynamic config overrides (from YAML)
        for k, v in kwargs.items():
            setattr(self, k, v)
