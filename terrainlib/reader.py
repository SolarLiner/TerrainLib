import abc
import numpy
from PIL import Image

from .terrain import Terrain


class TerrainReader(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __call__(self, terrain, *args, **kwargs):
        """Caller to process terrain data and output it into another format."""


class PILReader(TerrainReader):
    def __call__(self, terrain):
        arr = numpy.array(terrain._heightmap, dtype=float)
        return Image.fromarray(arr, mode='F')
        