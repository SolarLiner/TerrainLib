import abc
import numpy
from PIL import Image

from .terrain import Terrain


class TerrainReader(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __call__(self, terrain: Terrain, *args, **kwargs):
        """Caller to process terrain data and output it into another format."""


class PILReader(TerrainReader):
    BITDEPTH_FLOAT = (1., 'F', float)
    BITDEPTH_32 = (2**32-1, 'I', 'uint32')
    BITDEPTH_16 = (2**16-1, 'I', 'uint16')
    BITDEPTH_8 = (2**8-1, 'L', 'uint8')
    
    def __init__(self, bitdepth: tuple):
        if not bitdepth in [self.BITDEPTH_8, self.BITDEPTH_16, self.BITDEPTH_32, self.BITDEPTH_FLOAT]:
            raise TypeError('Bitdepth should be a valid number')
        self.bitdepth = bitdepth

    def __call__(self, terrain: Terrain):
        arr = numpy.array(terrain._heightmap, dtype='float32')
        depth, mode, dtype = self.bitdepth
        mult_arr = numpy.multiply(arr, depth)
        return Image.fromarray(numpy.array(mult_arr, dtype=dtype), mode)