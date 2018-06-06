import abc
import array
import logging
import random
from itertools import product

import numpy
from PIL import Image

logger = logging.getLogger(__name__)


def clamp(value, bounds=(0,1)):
    if bounds[0] > value:
        return bounds[0]
    if bounds[1] < value:
        return bounds[1]
    return value

class Terrain:
    def __init__(self, size):
        self._size = size
        self._heightmap = [[0 for _ in range(size)] for _ in range(size)]

    @property
    def size(self):
        return self._size

    def __getitem__(self, key):
        return self._heightmap[int(key[1] % self.size)][int(key[0] % self.size)]

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
                res[x,y] = clamp(self[x,y] + other)
            return res
        if isinstance(other, Terrain):
            for x,y in product(range(self.size), repeat=2):
                res[x,y] = clamp(self[x,y] + other[x,y])
            return res
        raise ArithmeticError("Type %s cannot add to type Terrain" % type(other).__name__)

    def __sub__(self, other):
        res = Terrain(self.size)
        if isinstance(other, (int, float)):
            return self + (-other)
        if isinstance(other, Terrain):
            for x,y in product(range(self.size), repeat=2):
                res[x,y] = clamp(self[x,y] - other[x,y])
            return res
        raise ArithmeticError("Type %s cannot subtract to type Terrain" % type(other).__name__)

    def __mul__(self, other):
        res = Terrain(self.size)
        if isinstance(other, (int, float, bool)):
            for x,y in product(range(self.size), repeat=2):
                res[x,y] = clamp(self[x,y] * other)
            return res
        if isinstance(other, Terrain):
            for x,y in product(range(self.size)):
                res[x,y] = clamp(self[x,y] * other[x,y])
            return res
        raise ArithmeticError("Type %s cannot multiply to type Terrain" % type(other).__name__)

    def __str__(self):
        return "Terrain object of size {}".format(self.size)

    def __repr__(self):
        return '\n'.join([str(self._heightmap[i]) for i in range(self.size)])


class TerrainGenerator(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __call__(self, *args, **kwargs):
        """Generates a terrain."""


class DiamondSquareGenerator(TerrainGenerator):
    def __init__(self, size: int, roughness: float):
        self.side_length = (2**size)+1
        self.terrain = [[0 for _ in range(self.side_length)] for _ in range(self.side_length)]
        self.roughness = roughness

    def __call__(self):
        self.setup_terrain()
        self.divide(self.side_length-1)
        return self.gen_terrain()

    def gen_terrain(self):
        terrain = Terrain(self.side_length)
        height_scale = self.side_length-1
        minimum = min([min(l) for l in self.terrain])
        maximum = max([max(l) for l in self.terrain]) - minimum
        for y in range(self.side_length):
            for x in range(self.side_length):
                terrain[x,y] = (self.terrain[x][y] - minimum) / maximum
        return terrain

    def divide(self, size: int):
        id = size // 2
        scale = self.roughness * size
        
        if id < 1:
            return
        
        # TODO: Remove this debug nonsense
        img = Image.fromarray(numpy.array(self.terrain, dtype=float), mode='F')
        img.convert('RGB', dither=None).save('terrain_size_{}.png'.format(size))
        
        # Squares
        for y in range(id, self.side_length-1, size):
            for x in range(id, self.side_length-1, size):
                s_scale = random.uniform(-scale, scale)
                self.square(x,y, id, s_scale)

        # Diamonds
        for y in range(0, self.side_length-1, size):
            for x in range((y+id) % size, self.side_length-1, size):
                d_scale = random.uniform(-scale, scale)
                self.diamond(x,y, id, d_scale)

        self.divide(id)

    def square(self, x, y, size, offset):
        tl = self.terrain[x-size][y-size]
        tr = self.terrain[x-size][y+size]
        br = self.terrain[x+size][y+size]
        bl = self.terrain[x+size][y-size]

        average = ((tl + tr + bl + br) / 4)
        self.terrain[x][y] = average + offset

    def diamond(self, x, y, size, offset):
        t = self.terrain[x][y-size]
        l = self.terrain[x+size][y]
        b = self.terrain[x][y+size]
        r = self.terrain[x-size][y]

        average = ((t+l+b+r)/4)
        self.terrain[x][y] = average + offset

    def setup_terrain(self):
        logger.debug('Setting up terrain size %i', self.side_length)
        maximum = self.side_length - 1

        self.terrain[0][0] = random.uniform(-self.side_length, self.side_length)
        self.terrain[maximum][0] = random.uniform(-self.side_length, self.side_length)
        self.terrain[0][maximum] = random.uniform(-self.side_length, self.side_length)
        self.terrain[maximum][maximum] = random.uniform(-self.side_length, self.side_length)
