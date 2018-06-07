import abc
import array
import logging
import random
from itertools import product

import numpy
from PIL import Image

logger = logging.getLogger(__name__)


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


class TerrainGenerator(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __call__(self, *args, **kwargs):
        """Generates a terrain."""


class DiamondSquareGenerator(TerrainGenerator):
    def __init__(self, size: int, roughness: float):
        self.side_length = (2**size)+1
        self.grid = [[0 for _ in range(self.side_length)] for _ in range(self.side_length)]
        self.roughness = roughness

    def __call__(self):
        self.setup_terrain()
        self.divide(self.side_length-1)
        return self.gen_terrain()

    def gen_terrain(self):
        terrain = Terrain(self.side_length)
        arr = numpy.array(self.grid)
        minimum = numpy.min(arr)
        maximum = numpy.max(arr) - minimum

        arr = numpy.subtract(numpy.array(self.grid), minimum)
        arr = numpy.divide(arr, maximum)

        terrain._heightmap = arr.tolist()
        return terrain

    def divide(self, size: int):
        id = size // 2
        if id < 1:
            return
        scale = self.roughness * size

        # TODO: Remove this debug nonsense!
        from .reader import PILReader
        img_reader = PILReader(PILReader.BITDEPTH_8)
        img = img_reader(self.gen_terrain())
        img.save('terrain_out_{}.png'.format(size))
        
        # Squares
        for y in range(id, self.side_length-1, size):
            for x in range(id, self.side_length-1, size):
                s_offset = random.uniform(-scale, scale)
                self.square(x,y, id, s_offset)

        # Diamonds
        for y in range(0, self.side_length-1, size):
            for x in range((y+id) % size, self.side_length-1, size):
                d_offset = random.uniform(-scale, scale)
                self.diamond(x,y, id, d_offset)

        self.divide(id)

    def square(self, x, y, size, offset):
        tl = self.grid[x-size][y-size]
        tr = self.grid[x-size][y+size]
        br = self.grid[x+size][y+size]
        bl = self.grid[x+size][y-size]

        average = ((tl + tr + bl + br) / 4)
        self.grid[x][y] = average + offset

    def diamond(self, x, y, size, offset):
        t = self.grid[x][y-size]
        l = self.grid[x+size][y]
        b = self.grid[x][y+size]
        r = self.grid[x-size][y]

        average = ((t+l+b+r)/4)
        self.grid[x][y] = average + offset

    def setup_terrain(self):
        logger.debug('Setting up terrain size %i', self.side_length)
        maximum = self.side_length - 1

        self.grid[0][0] = random.uniform(-self.side_length, self.side_length)
        self.grid[maximum][0] = random.uniform(-self.side_length, self.side_length)
        self.grid[0][maximum] = random.uniform(-self.side_length, self.side_length)
        self.grid[maximum][maximum] = random.uniform(-self.side_length, self.side_length)


class ImageGenerator(TerrainGenerator):
    BITDEPTH_FLOAT = 1
    BITDEPTH_32 = 2**32-1
    BITDEPTH_16 = 2**16-1
    BITDEPTH_8 = 2**8-1

    def __init__(self, img, bitdepth):
        if not bitdepth in [self.BITDEPTH_8, self.BITDEPTH_16, self.BITDEPTH_32, self.BITDEPTH_FLOAT]:
            raise TypeError('Bitdepth should be a valid number')
        self.bitdepth = bitdepth

        if isinstance(img, str):
            size = self._setup_image(Image.open(img), bitdepth)
        elif isinstance(img, Image.Image):
            size = self._setup_image(img, bitdepth)
        else:
            raise TypeError("Image can only be a string or a PIL.Image instance.")

        self.terrain = Terrain(size)

    def __call__(self):
        self.terrain._heightmap = self.data.tolist()

        return self.terrain

    def _setup_image(self, image, bitdepth):
        if isinstance(image, Image.Image):
            width, height = image.size  # type: (int, int)
            short_side = min(width, height)   # type: int

            left = (width - short_side) / 2
            right = (width + short_side) / 2
            top = (height - short_side) / 2
            bottom = (height + short_side) / 2

            cropped_img = image.crop((left, top, right, bottom))
            self.data = numpy.divide(numpy.array(cropped_img, order='F'), bitdepth) # type: numpy.ndarray

            return short_side