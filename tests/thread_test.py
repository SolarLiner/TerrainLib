""""""
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
import threading
from typing import Any, Dict, List

import numpy

from terrainlib.terrain import Terrain
from terrainlib.thread import BaseThreaded, BaseTiled, Size, Tile


class ThreadedAverageReader(BaseThreaded):
    def __init__(self):
        super().__init__()
        self.array = []
        self.lock = threading.Lock()

    def __call__(self, arrays: List[numpy.ndarray]):
        for i in arrays:
            self.put(i)
        super().__call__()
        self.join()
        return numpy.sum(self.array) / len(self.array)

    def task(self, *values):
        avg = 0
        for val in values:
            avg += numpy.sum(val) / val.shape
        with self.lock:
            self.array.append(avg)


class TiledAverageReader(BaseTiled):
    """Returns the average height of a Terrain object."""

    def __init__(self):
        super().__init__(32)

    def process_tile(self, terrain: Terrain, tile: Tile, size: Size):
        terr_slice = (slice(tile.x, tile.x + size.x), slice(tile.y, tile.y + size.y))
        arr = terrain.to_array()  # TODO: Use Terrain.__getitem__ once slices are accepted
        return numpy.sum(arr[terr_slice]) / (size.x * size.y)

    def process_results(self, results: Dict[Tile, Any]):
        values = list(results.values())
        return numpy.sum(values) / len(values)


class TestBaseThreaded:
    def setup(self):
        self.threaded = ThreadedAverageReader()

    def test_threads_completes(self):
        arr_in = [numpy.random.uniform(-10, 10, size=64) for _ in range(64)]
        avg = self.threaded(arr_in)
        assert numpy.isclose(avg, 0, atol=0.1).all()


class TestBaseTiled:
    def setup(self):
        self.tiled = TiledAverageReader()

    def test_tiles_runs(self):
        arr_size = 10
        results = numpy.zeros(shape=arr_size)
        for i, _ in enumerate(results):
            arr = numpy.random.uniform(-100, 100, size=(512, 512))
            avg = self.tiled(Terrain(array=arr))
            print('iteration %i: %f' % (i + 1, avg))
            results[i] = avg

        avg_avg = numpy.sum(results) / arr_size
        print('total average:', avg_avg)
        assert numpy.isclose(avg_avg, 0, atol=0.1).all()
