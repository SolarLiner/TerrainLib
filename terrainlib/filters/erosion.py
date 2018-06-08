"""Generators generally lack the kind of realism much needed in many different fields of science, media and
entertainment. Erosion is the main power sculpting the landscapes away. They smooth landscapes, create river beds, and
all other kind of goodies that elevate a terrain from 'just nice' to 'completely unbeliveable'."""
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
from itertools import product

import numpy

from ..terrain import Terrain
from .base import TerrainFilter

logger = logging.getLogger(__name__)

def north(matrix):
    """Return a matrix moved one line north, wrapping around the grid."""
    return numpy.concatenate((matrix[1:,:], matrix[:1,:]))

def east(matrix):
    """Return a matrix moved one line east, wrapping around the grid."""
    return numpy.concatenate((matrix[:,-1:], matrix[:,:-1]), 1)

def south(matrix):
    """Return a matrix moved one line south, wrapping around the grid."""
    return numpy.concatenate((matrix[-1:,:], matrix[:-1,:]))

def west(matrix):
    """Return a matrix moved one line west, wrapping around the grid."""
    return numpy.concatenate((matrix[:,1:], matrix[:,:1]), 1)

def sign(x, bias=0.001):
    """Returns the sign of the number, with bias."""
    if x < bias:
        return -1
    if x > bias:
        return 1
    return 0
vsign = numpy.vectorize(sign)

class HydraulicErosionFilter(TerrainFilter):
    """Hydraulic erosion occurs when the motion of water against a rock surface produces mechanical
    weathering. Most generally, it is the ability of moving water (flowing or waves) to dislodge and transport rock
    particles. Within this rubric are a number of specific erosional processes, including abrasion, attrition,
    corrasion, saltation, and scouring (downcutting). Hydraulic action is distinguished from other types of water
    facilitated erosion, such as static erosion where water leaches salts and floats off organic material from
    unconsolidated sediments, and from chemical erosion more often called chemical weathering. It is a mechanical
    process, in which the moving water current flows against the banks and bed of a river, thereby removing rock
    particles.

    Source: https://en.wikipedia.org/wiki/Hydraulic_action"""
    FLAT = 0.01
    def __init__(self, iterations: int, rain_amt=0.01, solubility=0.1, capacity=0.5, evaporation=0.3):
        """Initialize hydraulic erosion weathering.

        :param iterations: Number of repeated times the algorithm will be ran. Values below 50 typically do not yeild
        satisfying results.
        :param rain_amt: Amount of rain that falls on the map at each iteration.
        :param solubility: Amount of terrain dissolving into water at each iteration.
        :param capacity: Amount of soil that can be contained in water.
        :param evaporation: Amount of water that evaporates after each iteration.
        """
        self.rainfall = max(0.01, min(1., rain_amt))
        self.iterations = max(2, iterations)
        self.solubility = max(0.01, min(1., solubility))
        self.evaporation = max(0.01, min(1., evaporation))
        self.capacity = max(0.01, min(1., capacity))

    def __call__(self, terrain: Terrain):
        """Runs the erosion algorithm with the input Terrain object.

        Additional data is available once the simulation has run:
        - A difference map ``HydraulicErosionFilter.difference_map`` tracks the changes from original to eroded
        - A sediment map ``HydraulicErosionFilter.sediment_map`` shows where sediment has been deposited
        - A water map ``HydraulicErosionFilter.water_map`` shows where water has flowed

        :param terrain: Terrain object to apply erosion to.
        :returns: new Terrain object with erosion applied"""
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


class ThermalErosionFilter(TerrainFilter):
    """Thermal weathering is caused by temperature changes causing small portions of the material to crumble and pile
    up on the bottom of an incline. The thermal weathering erosion ends the slopes of uniform angles.

    Source: http://old.cescg.org/CESCG97/marak/node11.html"""
    def __init__(self, iterations: int, power=.5, talus=1.):
        """Initialize the thermal erosion algorithm.

        :param iterations: Number of successive times the algorithm will be run. The more, the better.
        :param power: Amount of soil falling downhill.
        :param talus: Critical angle over which soil will fall.
        """
        self.talus = talus / 1000.
        self.iterations = max(10, iterations)
        self.erosion = max(.01, min(1., power))

    def __call__(self, terrain: Terrain):
        """Runs the algorithm over the input Terrain object.

        :param terrain: Terrain object to be eroded.
        :returns: new Terrain object with eroded terrain.
        """
        heights = numpy.array(terrain._heightmap)
        for i in range(self.iterations):
            logger.info('Thermal erosion %.1f%%', 100*i/self.iterations)
            heights = self.erode_once(heights)

        new_terrain = Terrain(terrain.size)
        new_terrain._heightmap = heights.tolist()
        return new_terrain

    def erode_once(self, heights: numpy.ndarray):
        """Erode once. Should not be called directly.

        :param heights: 2D numpy array containing the heights of the terrain at each grid point."""
        nsew = [(heights - x(heights)).clip(0., 1.) for x in (north, east, south, west)]
        nsew = [(x - x.clip(-self.talus, self.talus)) for x in nsew]
        
        arr = heights - sum(nsew) * (self.erosion / 4.0)
        return arr
