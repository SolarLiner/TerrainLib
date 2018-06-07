import abc
import numpy
from PIL import Image

from .terrain import Terrain


class TerrainReader(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __call__(self, terrain, *args, **kwargs):
        """Caller to process terrain data and output it into another format."""


class PILReader(TerrainReader):
    BITDEPTH_FLOAT = 1
    BITDEPTH_32 = 2**32-1
    BITDEPTH_16 = 2**16-1
    BITDEPTH_8 = 2**8-1
    
    def __init__(self, bitdepth=BITDEPTH_16):
        if not bitdepth in [self.BITDEPTH_8, self.BITDEPTH_16, self.BITDEPTH_32, self.BITDEPTH_FLOAT]:
            raise TypeError('Bitdepth should be a valid number')
        self.bitdepth = bitdepth

    def __call__(self, terrain):
        arr = numpy.array(terrain._heightmap, dtype=float)
        return Image.fromarray(numpy.multiply(arr, self.bitdepth, 'F')