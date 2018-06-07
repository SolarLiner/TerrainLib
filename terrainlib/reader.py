import abc
import numpy
from PIL import Image

from .terrain import Terrain


class TerrainReader(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __call__(self, terrain: Terrain, *args, **kwargs):
        """Caller to process terrain data and output it into another format."""


class PILReader(TerrainReader):
    BITDEPTH_FLOAT = 1
    BITDEPTH_32 = 2**32-1
    BITDEPTH_16 = 2**16-1
    BITDEPTH_8 = 2**8-1
    
    def __init__(self, bitdepth: int):
        if not bitdepth in [self.BITDEPTH_8, self.BITDEPTH_16, self.BITDEPTH_32, self.BITDEPTH_FLOAT]:
            raise TypeError('Bitdepth should be a valid number')
        self.bitdepth = bitdepth

    def __call__(self, terrain: Terrain):
        arr = numpy.array(terrain._heightmap, dtype=float)
        if self.bitdepth == self.BITDEPTH_FLOAT:
            mode = 'F'
        elif self.bitdepth == self.BITDEPTH_8:
            mode = 'L'
        else:
            mode = 'I'
        return Image.fromarray(numpy.multiply(arr, self.bitdepth), mode)