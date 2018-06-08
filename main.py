import logging
from itertools import product

import numpy
from PIL import Image

from terrainlib.generators.procedural import DiamondSquareGenerator
from terrainlib.generators.image import PILInputGenerator
from terrainlib.filters.erosion import ThermalErosionFilter, HydraulicErosionFilter
from terrainlib.readers.image import PILImageReader

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)


def main():
    # generator = DiamondSquareGenerator(10, 0.5)
    generator = PILInputGenerator('data/terrain_in.png', PILInputGenerator.BITDEPTH_8)
    hydrerode = HydraulicErosionFilter(100)
    thermal_erode = ThermalErosionFilter(500)
    img_reader = PILImageReader(PILImageReader.BITDEPTH_8)

    terr = hydrerode(generator())
    img_reader(terr).save('terrain_out_hydrolic.png')
    terr = thermal_erode(terr)
    img_reader(terr).save('terrain_out.png')


if __name__ == '__main__':
    main()
