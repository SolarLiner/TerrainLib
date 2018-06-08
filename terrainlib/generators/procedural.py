"""Procedural generators allow for unlimited sizes and details as they can generate anything, but they also take the
longest to actually run generation. Tradeoffs, tradeoffs everywhere!"""
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

import logging
import random

import numpy

from ..terrain import Terrain
from .base import TerrainGenerator

logger = logging.getLogger(__name__)


class DiamondSquareGenerator(TerrainGenerator):
    """The diamond-square algorithm is a method for generating heightmaps for computer graphics. It is a slightly better
    algorithm than the three-dimensional implementation of the midpoint displacement algorithm which produces 
    two-dimensional landscapes. It is also known as the random midpoint displacement fractal, the cloud fractal or the 
    plasma fractal, because of the plasma effect produced when applied.

    The idea was first introduced by Fournier, Fussell and Carpenter at SIGGRAPH 1982.

    The diamond-square algorithm starts with a 2D grid then randomly generates terrain height from four seed values
    arranged in a grid of points so that the entire plane is covered in squares.

    Source: https://en.wikipedia.org/wiki/Diamond-square_algorithm"""

    def __init__(self, size: int, roughness: float):
        """Initialize the Diamond Square generator.

        :param size: As Diamond Square needs a `2**n+1` sized grid, the size is simply the exponent of the power of two.
        :param roughness: Fraction of the size of the square at each iteration, that will be used as bounds for the
        random offset. Traditional values sit between 0.01 for flat landscapes, to 0.3 for rough hills. Anything above
        will produce unrealistic terrain and should only be used for abstract art.

        :Example:
        ``generator = DiamondSquareGenerator(10, 0.1)   # Generates a 1025-sized grid with roughness of 0.1``
        """
        self.side_length = (2**size)+1
        self.terrain = Terrain(self.side_length)
        self.roughness = roughness

    def __call__(self):
        """Generates the terrain. Takes no additional arguments, as all input parameters have been set in the init call.
        """
        self._setup_terrain()
        self._divide(self.side_length-1)
        return self._gen_terrain()

    def _gen_terrain(self):
        """Setups the algorithm with proper size. Should not be called from outside."""
        arr = numpy.array(self.terrain._heightmap)
        minimum = numpy.min(arr)
        maximum = numpy.max(arr) - minimum

        arr = numpy.subtract(arr, minimum)
        arr = numpy.divide(arr, maximum)

        self.terrain._heightmap = arr.tolist()
        return self.terrain

    def _divide(self, size: int):
        """Recursive function that applies the diamond square process through the entire grid. Should not be called
        directly.
        
        :param size: Current iteration size
        """
        id = size // 2
        if id < 1:
            return
        scale = self.roughness * size
        
        # Squares
        for y in range(id, self.side_length-1, size):
            for x in range(id, self.side_length-1, size):
                self._square(x,y, id, scale)

        # Diamonds
        for y in range(0, self.side_length-1, size):
            for x in range(0, self.side_length-1, size):
                self._diamond(x+id,y, id, scale)
                self._diamond(x,y+id, id, scale)

        self._divide(id)

    def _square(self, x: int, y: int, size: int, scale: float):
        """Performs the square step of the generation algorithm. Should not be called directly.

        :param x: X position on the grid
        :param y: Y position on the grid
        :param size: current iteration square size
        :param scale: current iteration random bounds scaling value
        """
        tl = self.terrain[x-size,y-size]
        tr = self.terrain[x-size,y+size]
        br = self.terrain[x+size,y+size]
        bl = self.terrain[x+size,y-size]

        average = ((tl + tr + bl + br) / 4)
        offset = random.uniform(-scale, scale)        
        self.terrain[x,y] = average + offset

    def _diamond(self, x: int, y: int, size: int, scale: float):
        """Performs the diamond step of the generation algorithm. Should not be called directly.

        :param x: X position on the grid
        :param y: Y position on the grid
        :param size: current iteration square size
        :param scale: current iteration random bounds scaling value
        """
        t = self.terrain[x,y-size]
        l = self.terrain[x+size,y]
        b = self.terrain[x,y+size]
        r = self.terrain[x-size,y]

        average = ((t+l+b+r)/4.0)
        offset = random.uniform(-scale, scale)
        self.terrain[x,y] = average + offset

    def _setup_terrain(self):
        """Setups the terrain for generation. Should not be called directly."""
        logger.debug('Setting up terrain size %i', self.side_length)
        maximum = self.side_length - 1

        self.terrain[0,0] = random.uniform(-self.side_length, self.side_length)
        self.terrain[maximum,0] = random.uniform(-self.side_length, self.side_length)
        self.terrain[0,maximum] = random.uniform(-self.side_length, self.side_length)
        self.terrain[maximum,maximum] = random.uniform(-self.side_length, self.side_length)
