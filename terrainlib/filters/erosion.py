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

import numpy
import numexpr

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

def north_east(matrix):
    return east(north(matrix))

def north_west(matrix):
    return west(north(matrix))

def south_west(matrix):
    return west(south(matrix))

def south_east(matrix):
    return east(south(matrix))

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

    def __init__(self, iterations: int, delta_t=0.01, rain_amt=0.012, solubility=0.1, capacity=1., evaporation=.015):
        """Initialize hydraulic erosion weathering.

        :param iterations: Number of repeated times the algorithm will be ran. Values below 50 typically do not yeild
        satisfying results.
        :param rain_amt: Amount of rain that falls on the map at each iteration.
        :param solubility: Amount of terrain dissolving into water at each iteration.
        :param capacity: Amount of soil that can be contained in water.
        :param evaporation: Amount of water that evaporates after each iteration.
        """
        self.rainfall = max(0.001, min(.05, rain_amt))
        self.iterations = max(2, iterations)
        self.evaporation = max(0.001, min(.05, evaporation))
        self.capacity = max(0.1, min(3., capacity))

    def __call__(self, terrain: Terrain):
        """Runs the erosion algorithm with the input Terrain object.

        Additional data is available once the simulation has run:
        - A difference map ``HydraulicErosionFilter.difference_map`` tracks the changes from original to eroded
        - A sediment map ``HydraulicErosionFilter.sediment_map`` shows where sediment has been deposited
        - A water map ``HydraulicErosionFilter.water_map`` shows where water has flowed

        :param terrain: Terrain object to apply erosion to.
        :returns: new Terrain object with erosion applied"""
        scale = 512     # TODO: Take that value from terrain properties
        b = numpy.array(terrain._heightmap)
        d = numpy.zeros(b.shape)
        s = numpy.zeros(b.shape)
        f = numpy.zeros((4,) + b.shape)     # [west, east, north, south]
        v = numpy.zeros((2,) + b.shape)

        dt = .01
        Kr = self.rainfall
        Ke = self.evaporation
        A  = 20
        g  = 9.81
        Kc = self.capacity
        Kt = .15
        Ks = .5
        Kd = 1
        Kh = 5
        Kdmax = 10
        Ka = .8
        Ki = .1
        l = 1   # TODO: Take that value from terrain properties

        for i in range(self.iterations):
            logger.info('%i%% - Iteration %i', 100*i//self.iterations, i+1)
            d1 = d + dt * Kr
            tf = numpy.zeros(d.shape)
            for i,dir in enumerate([west, east, north, south]):
                dh = b + d1 - dir(b) - dir(d1)
                f[i] = numpy.maximum(0.0, f[i] + dt * A * (numpy.divide(g * dh, l)))
                tf = numpy.add(tf, f[i])
            K = numpy.maximum(1., numpy.divide(d1*l*l, tf * dt))
            f = numpy.multiply(f, K)

            fin = [dir(f[i]) for i, dir in enumerate((west, east, north, south))]
            fin = numpy.reshape(fin, d.shape + (4,))
            dV = dt * (numpy.sum(fin, 2) - numpy.sum(numpy.reshape(f, d.shape + (4,), 2)))
            logger.debug('dV: %s - d: %s', repr(dV.shape), repr(d.shape))
            d = d + numpy.divide(dV, l*l)

            d *= 1 - Ke
            b += d * Ke * Kc

        return Terrain(array=b)



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

        return Terrain(array=heights)

    def erode_once(self, heights: numpy.ndarray):
        """Erode once. Should not be called directly.

        :param heights: 2D numpy array containing the heights of the terrain at each grid point."""
        nsew = [(heights - x(heights)).clip(0., 1.) for x in (north, north_east, east, south_east, south, south_west, west)]
        nsew = [(x - x.clip(-self.talus, self.talus)) for x in nsew]
        
        arr = heights - sum(nsew) * (self.erosion / 8.0)
        return arr


class StrataErosionFilter(TerrainFilter):

    def __init__(self, number=5.0):
        self.levels = float(max(2., number))

    def __call__(self, terrain: Terrain):
        heights = numpy.multiply(terrain._heightmap, self.levels)

        return Terrain(array=heights)