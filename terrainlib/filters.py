"""Filters apply transformations to the terrain."""
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
import logging
import numpy
from itertools import product
from .terrain import Terrain

logger = logging.getLogger(__name__)


class TerrainFilter(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __call__(self, terrain):
        """Apply transform onto the terrain. Must output terrain afterwards."""

def north(matrix):
    return numpy.concatenate((matrix[1:,:], matrix[:1,:]))

def east(matrix):
    return numpy.concatenate((matrix[:,-1:], matrix[:,:-1]), 1)

def south(matrix):
    return numpy.concatenate((matrix[-1:,:], matrix[:-1,:]))

def west(matrix):
    return numpy.concatenate((matrix[:,1:], matrix[:,:1]), 1)

def sign(x):
    if x < 0.001:    # Adding bias otherwise function will never output 0
        return -1
    if x > 0.001:
        return 1
    return 0
vsign = numpy.vectorize(sign)


class ThermalErosionFilter(TerrainFilter):
    def __init__(self, iterations: int, power=.5, talus=1.):
        self.talus = talus / 1000.
        self.iterations = max(10, iterations)
        self.erosion = max(.01, min(1., power))

    def __call__(self, terrain: Terrain):
        heights = numpy.array(terrain._heightmap)
        for i in range(self.iterations):
            logger.info('Thermal erosion %.1f%%', 100*i/self.iterations)
            heights = self.erode_once(heights)

        new_terrain = Terrain(terrain.size)
        new_terrain._heightmap = heights.tolist()
        return new_terrain

    def erode_once(self, heights: numpy.ndarray):
        nsew = [(heights - x(heights)).clip(0., 1.) for x in (north, east, south, west)]
        nsew = [(x - x.clip(-self.talus, self.talus)) for x in nsew]
        
        arr = heights - sum(nsew) * (self.erosion / 4.0)
        return arr


class HydraulicErosionFilter(TerrainFilter):
    FLAT = 0.01
    def __init__(self, iterations: int, rain_amt=0.01, solubility=0.1, capacity=0.5, evaporation=0.3):
        self.rainfall = max(0.01, min(1., rain_amt))
        self.iterations = max(2, iterations)
        self.solubility = max(0.01, min(1., solubility))
        self.evaporation = max(0.01, min(1., evaporation))
        self.capacity = max(0.01, min(1., capacity))

    def __call__(self, terrain: Terrain):
        heights = numpy.array(terrain._heightmap)
        shape = heights.shape
        difference = numpy.zeros(shape)
        sediment = numpy.zeros(shape)
        water = numpy.zeros(shape)

        for i in range(self.iterations):
            logger.info('Hydraulic erosion %.1f%%', 100*i/self.iterations)
            # Step 1: rainfall
            water += self.rainfall
            # Step 2: erosion
            heights -= self.solubility
            sediment += self.solubility
            # Step 3: movement
            grad_x, grad_y = numpy.gradient(heights+water)
            for x,y in product(range(terrain.size), repeat=2):  # TODO: Thread the sh*t out of this
                water_height = (heights+water)[x,y]
                neighbor = (x + sign(grad_x[x,y]), y + sign(grad_y[x,y]))

                if (x,y) == neighbor:   # Only continue if the water needs to go somewhere
                    continue
                water_height_nbr = (heights+water)[neighbor]

                water[neighbor] += water[x,y]
                water[x,y] = 0
            # Step 4: evaporation
            water *= 1 - self.evaporation
            difference = numpy.maximum(self.capacity - sediment, numpy.zeros(shape))
            sediment -= difference
            heights += difference

        self.sediments_map = sediment
        self.water_map = water
        self.difference_map = difference



