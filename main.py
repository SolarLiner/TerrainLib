from datetime import timedelta
import logging
from itertools import product
import time

import numpy
from PIL import Image

from terrainlib.generators.procedural import DiamondSquareGenerator, VoronoiGenerator
from terrainlib.generators.image import PILInputGenerator
from terrainlib.filters.erosion import ThermalErosionFilter, HydraulicErosionFilter, StrataErosionFilter
from terrainlib.readers.image import PILImageReader


class ElapsedFormatter(logging.Formatter):
    def __init__(self, fmt=None):
        super().__init__(fmt)
        self.start = time.time()

    def format(self, record):
        message = super(__class__, self).format(record)
        elapsed_time = timedelta(seconds=record.created - self.start)
        return '[{} s] {}'.format(elapsed_time, message)

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

sh = logging.FileHandler('debug.log', 'w')
sh.setFormatter(ElapsedFormatter('%(levelname)s @ %(module)s: %(message)s'))

def main():
    generator = PILInputGenerator('data/terrain_in.png', PILInputGenerator.BITDEPTH_16)
    eroder = HydraulicErosionFilter(500)
    reader = PILImageReader(PILImageReader.BITDEPTH_8)

    terr = eroder(generator())
    img = reader(terr)
    img.save('terrain_out.png')


if __name__ == '__main__':
    main()
