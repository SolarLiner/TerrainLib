# TerrainLib - A fast terrain generation library
# Copyright © 2018  Nathan "SolarLiner" Graule

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
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