"""Abstract class definitions to setup the convention of Terrain Filters."""
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
from itertools import repeat
from threading import Lock
from typing import Dict, Tuple

import numpy

from ..queue import BaseThreaded
from ..terrain import Terrain


class TerrainFilter(metaclass=abc.ABCMeta):
    """Modifies a Terrain object. This base class does not support threading. To allow threading in your algorithms,
    use :class:`TerrainThreadedFilter`. """

    @abc.abstractmethod
    def __call__(self, terrain, *args, **kwargs):
        """Apply transform onto the terrain. Must output terrain afterwards."""


class TerrainThreadedFilter(TerrainFilter, BaseThreaded, metaclass=abc.ABCMeta):
    """Terrain filter that can be tiled and therefore can be threaded to use multiple cores of a CPU (or even use
    multiple CPUs)."""
    tile_size: int
    results: Dict[Tuple[int, int], Terrain]
    results_mutex: Lock

    def __init__(self, tile_size: int):
        super().__init__()
        self.tile_size = tile_size
        self.results = []
        self.results_mutex = Lock()

    def __call__(self, terrain: Terrain, *args, **kwargs):
        super(BaseThreaded).__call__()
        tile_count = terrain.size // self.tile_size
        for x, y in repeat(range(tile_count), 2):
            tile_x = self.tile_size * x
            tile_end_x = tile_x + self.tile_size if x < tile_count - 1 else terrain.size
            tile_y = self.tile_size * y
            tile_end_y = tile_y + self.tile_size if x < tile_count - 1 else terrain.size
            slice_x = slice(tile_x, tile_end_x)
            slice_y = slice(tile_y, tile_end_y)
            tile = terrain[slice_x, slice_y]
            self.put((tile, tile_x, tile_y))
        self.join()  # Awaits completion of the filter

        arr = numpy.zeros((terrain.size, terrain.size))
        for (tile_x, tile_y), v in self.results.items():
            slice_x = slice(self.tile_size * tile_x, self.tile_size * (tile_x + 1))
            slice_y = slice(self.tile_size * tile_y, self.tile_size * (tile_y + 1))
            # Technically since the array is only written to and not read, this should not matter. Defensive
            # programming does call for this mutex anyway since the array can unfortunately be accessed from the
            # outside due to Python implementation of OO.
            with self.results_mutex:
                arr[slice_x, slice_y] = v.to_array()

        return Terrain(array=arr)

    @abc.abstractmethod
    def process_threaded(self, tile: Terrain, tile_x: int, tile_y: int) -> Terrain:
        """Process the Terrain tile. Runs in a separate thread. """

    def task(self, tile: Terrain, tile_x: int, tile_y: int):
        result = self.process_threaded(tile, tile_x, tile_y)
        self.results[(tile_x, tile_x)] = result
