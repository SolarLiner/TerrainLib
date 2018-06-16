"""The Terrain class contains the object type that will hold all necessary, Terrain-related data to pass from function
to function."""

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
from itertools import product



class Terrain:
    def __init__(self, size):
        self._size = size
        self._heightmap = [[0 for _ in range(size)] for _ in range(size)]

    @property
    def size(self):
        return self._size

    def __getitem__(self, key):
        if isinstance(key[0], int):
            cols = self._heightmap[key[0]]
        if isinstance(key[0], float):
            cols = self._heightmap[int(key[0]) % self.size]
            next_cols = self._heightmap[int(key[0] + 1) % self.size]
            frac_part = key[0] - int(key[0])
            cols = frac_part * next_cols + (1.0 - frac_part) * cols

    def __setitem__(self, key, value):
        self._heightmap[key[1] % self.size][key[0] % self.size] = value

    def __eq__(self, other):
        if isinstance(other, Terrain):
            if not other.size == self.size:
                return False
            return all(self[x,y] == other[x,y] for x in range(self.size) for y in range(self.size))
        return False

    def __add__(self, other):
        res = Terrain(self.size)
        if isinstance(other, (int, float)):
            for x,y in product(range(self.size), repeat=2):
                res[x,y] = self[x,y] + other
            return res
        if isinstance(other, Terrain):
            for x,y in product(range(self.size), repeat=2):
                res[x,y] = self[x,y] + other[x,y]
            return res
        raise ArithmeticError("Type %s cannot add to type Terrain" % type(other).__name__)

    def __sub__(self, other):
        res = Terrain(self.size)
        if isinstance(other, (int, float)):
            return self + (-other)
        if isinstance(other, Terrain):
            for x,y in product(range(self.size), repeat=2):
                res[x,y] = self[x,y] - other[x,y]
            return res
        raise ArithmeticError("Type %s cannot subtract to type Terrain" % type(other).__name__)

    def __mul__(self, other):
        res = Terrain(self.size)
        if isinstance(other, (int, float, bool)):
            for x,y in product(range(self.size), repeat=2):
                res[x,y] = self[x,y] * other
            return res
        if isinstance(other, Terrain):
            for x,y in product(range(self.size)):
                res[x,y] = self[x,y] * other[x,y]
            return res
        raise ArithmeticError("Type %s cannot multiply to type Terrain" % type(other).__name__)

    def __str__(self):
        return "Terrain object of size {}".format(self.size)

    def __repr__(self):
        return '\n'.join([str(self._heightmap[i]) for i in range(self.size)])
