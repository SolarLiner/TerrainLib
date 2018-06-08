"""Export terrain to a greyscale image."""
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
import numpy
from PIL import Image

from .base import TerrainReader
from ..terrain import Terrain


class PILReader(TerrainReader):
    """Export terrain as a greyscale ``PIL.Image`` instance."""
    BITDEPTH_FLOAT = (1., 'F', float)
    BITDEPTH_32 = (2**32-1, 'I', 'uint32')
    BITDEPTH_16 = (2**16-1, 'I', 'uint16')
    BITDEPTH_8 = (2**8-1, 'L', 'uint8')
    
    def __init__(self, bitdepth: tuple):
        """Initialize a ``PIL.Image`` exporter.

        :param bitdepth: Bitdepth of the output image. One of ``PILReader.BITDEPTH_8, PILReader.BITDEPTH_16, PILReader.BITDEPTH_32, 
        PILReader.BITDEPTH_FLOAT``
        """
        if not bitdepth in [self.BITDEPTH_8, self.BITDEPTH_16, self.BITDEPTH_32, self.BITDEPTH_FLOAT]:
            raise TypeError('Bitdepth should be a valid number')
        self.bitdepth = bitdepth

    def __call__(self, terrain: Terrain):
        """Export the terrain to a ``PIL.Image`` instance.

        :param terrain: Terrain object to be exported.
        :returns: ``PIL.Image`` instance containing the greyscale image.
        """
        arr = numpy.array(terrain._heightmap, dtype='float32')
        depth, mode, dtype = self.bitdepth
        mult_arr = numpy.multiply(arr, depth)
        return Image.fromarray(numpy.array(mult_arr, dtype=dtype), mode)