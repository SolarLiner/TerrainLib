import abc
import numpy
from PIL import Image

from .terrain import Terrain


class TerrainReader(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __call__(self, terrain, *args, **kwargs):
        """Caller to process terrain data and output it into another format."""


class PILReader(TerrainReader):
    BITDEPTH_FLOAT = 0
    BITDEPTH_32 = 1
    BITDEPTH_16 = 2
    BITDEPTH_8 = 3
    
    def __init__(self, bitdepth=BITDEPTH_16):
        self.bitdepth = bitdepth

    def __call__(self, terrain):
        arr = numpy.array(terrain._heightmap, dtype=float)        
        if self.bitdepth == self.BITDEPTH_8:
            return Image.fromarray(numpy.multiply(arr, 255.0), 'L')
        if self.bitdepth == self.BITDEPTH_16:
            return Image.fromarray(numpy.multiply(arr, 2**16-1), 'I')
        if self.bitdepth == self.BITDEPTH_32:
            return Image.fromarray(numpy.multiply(arr, 2**32-1), 'I')
        return Image.fromarray(arr, 'F')