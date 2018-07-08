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
from typing import Any

import numpy


def lerp(x: float, a: Any, b: Any):
    """
    Linearly interpolate between two objects a and b, using control value x.
    :param x: Float control value. Values 0..1 interpolate, while values outside extrapolate.
    :param a: Object to be interpolated from. Must support multiplication with a float and addition with `type(b)`.
    :param b: Object to be interpolated to. Must support multiplication with a float and addition with `type(a)`.
    :return: Interpolated value, type of result a+b.
    """
    return x * b + (1.0 - x) * a


class Terrain:
    _heightmap: numpy.ndarray
    _size: int

    def __init__(self, size: int = None, array: numpy.ndarray = None):
        if array is not None:
            shape = numpy.shape(array)
            if not len(shape) == 2:
                raise TypeError('Input array should be 2-dimensional')
            if not shape[1] == shape[0]:
                raise TypeError('Input array should be square')
            self._heightmap = numpy.array(array)
            self._size = shape[0]
        elif size is not None:
            self._size = size
            self._heightmap = numpy.zeros((size, size))
        else:
            raise TypeError('Either size or input 2D array should be passed as input')

    def copy(self):
        """Copy the current Terrain object and returns it."""
        return Terrain(array=self._heightmap)

    def to_array(self):
        """Returns a copy of the numpy array."""
        return self._heightmap.copy()

    def to_list(self):
        """Returns a 1D list of the array. Use [j + i * size] to calculate the index."""
        return list(self._heightmap.reshape(self.size ** 2))

    @property
    def size(self) -> int:
        return self._size

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._heightmap[key]
        if isinstance(key, float):
            int_part = int(key)
            frac_part = key - int_part
            cols = self._heightmap[int_part]
            next_cols = self._heightmap[int_part + 1]
            return lerp(frac_part, cols, next_cols)
        if not isinstance(key, tuple):
            raise TypeError('Item key must either be int, float, or tuple of int, float, slice. %s received.' % str(
                    type(key)))

        if isinstance(key[0], slice) and isinstance(key[1], slice):
            return self._heightmap[key]
        if isinstance(key[0], (int, slice)):
            cols = self._heightmap[key[0]]
        if isinstance(key[0], float):
            cols = self._heightmap[int(key[0]) % self.size]
            next_cols = self._heightmap[int(key[0] + 1) % self.size]
            frac_part = key[0] - int(key[0])
            cols = lerp(frac_part, cols, next_cols)

        if isinstance(key[1], (int, slice)):
            val = cols[key[1]]
        if isinstance(key[1], float):
            val = cols[int(key[1]) % self.size]
            val_next = cols[int(key[1] + 1) % self.size]
            frac_part = key[1] - int(key[1])
            val = lerp(frac_part, val, val_next)

        return val

    def __setitem__(self, key, value):
        self._heightmap[key[1] % self.size, key[0] % self.size] = value

    def __eq__(self, other):
        if isinstance(other, Terrain):
            return numpy.equal(self._heightmap, other._heightmap)
        else:
            return numpy.equal(self._heightmap, other)

    def __add__(self, other):
        if isinstance(other, Terrain):
            res = numpy.add(self._heightmap, other._heightmap)
        else:
            res = numpy.add(self._heightmap, other)
        return Terrain(array=res)

    def __sub__(self, other):
        if isinstance(other, Terrain):
            res = numpy.subtract(self._heightmap, other._heightmap)
        else:
            res = numpy.subtract(self._heightmap, other)
        return Terrain(array=res)

    def __mul__(self, other):
        if isinstance(other, Terrain):
            res = numpy.multiply(self._heightmap, other._heightmap)
        else:
            res = numpy.multiply(self._heightmap, other)
        return Terrain(array=res)

    def __str__(self):
        return "Terrain(size={}): {}".format(self.size, str(self._heightmap))

    def __repr__(self):
        return repr(self._heightmap)
