"""Custom lightweight task queue for threaded processing."""
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
import os
import queue
from collections import namedtuple
from itertools import product
from threading import Lock, Thread
from typing import Any, Dict

from terrainlib.terrain import Terrain


class BaseThreaded(queue.Queue):
    """A task queue holds a list of tasks to be computed by a worker. Multiple workers can be made available,
    allowing tasks to be run in parallel. This is implemented as a base class"""
    num_workers: int

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.set_thread_count()

    def __call__(self, *args, **kwargs):
        self._start_workers()

    def set_thread_count(self, count=0):
        """Sets the number of threads, or get number from number of CPUs."""
        if count == 0:
            self.num_workers = os.cpu_count()
        else:
            self.num_workers = max(1, int(count))

    def task(self, *args, **kwargs):
        """Task that gets parallel processed."""
        raise NotImplementedError()

    def _start_workers(self):
        for _ in range(self.num_workers):
            t = Thread(target=self._worker)
            t.daemon = True
            t.start()

    def _worker(self):
        while True:
            item = self.get()
            if item is None:
                break
            if isinstance(item, dict):
                self.task(**item)
            elif isinstance(item, (list, tuple)):
                self.task(*item)
            else:
                self.task(item)

            self.task_done()


Tile = namedtuple('Tile', 'x y')
Size = namedtuple('Size', 'x y')


class BaseTiled(BaseThreaded):
    """Base class for tiled terrain processors.

    Derived classes must implement `process_tile` which processes a tile, and `process_all` to process the whole
    array of tiled results. If no process is needed, simply return the incoming array."""
    lock: Lock
    results: Dict[Tile, Any]

    def task(self, terrain: Terrain, tile: Tile, size: Size, **kwargs):
        result = self.process_tile(terrain, tile, size)
        with self.lock:
            self.results[tile] = result

    def __init__(self, tile_size: int):
        super().__init__()
        self.tile_size = max(16, tile_size)
        self.results = dict()
        self.lock = Lock()

    def __call__(self, terrain: Terrain, *args, **kwargs):
        for tile, size in self._get_tiles(terrain.size):
            self.put((terrain, tile, size))
        super().__call__(*args, **kwargs)
        self.join()

        return self.process_results(self.results.copy())

    def _get_tiles(self, terrain_size):
        tile_count = terrain_size // self.tile_size
        for i, j in product(range(tile_count), repeat=2):
            tile_x = self.tile_size * i
            tile_y = self.tile_size * j

            if tile_x + self.tile_size > terrain_size:
                size_x = terrain_size - tile_x
            else:
                size_x = self.tile_size

            if tile_y + self.tile_size > terrain_size:
                size_y = terrain_size - tile_x
            else:
                size_y = self.tile_size

            yield (Tile(tile_x, tile_y), Size(size_x, size_y))

    def process_tile(self, terrain: Terrain, tile: Tile, size: Size):
        raise NotImplementedError()

    def process_results(self, arr: Dict[Tile, Any]):
        raise NotImplementedError()
