from abc import ABC, abstractmethod

class BaseHandler(ABC):
    """Abstract base class for all plotting handlers."""

    def __init__(self, config):
        self.config = config

    @abstractmethod
    def load(self, ds):
        """Extract variable(s) from xarray Dataset."""
        pass

    @abstractmethod
    def plot(self, ax, data):
        """Plot extracted data."""
        pass
