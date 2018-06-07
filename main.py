import logging
from itertools import product

import numpy
from PIL import Image

from terrainlib import reader, terrain, filters

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)


def main():
    # generator = terrain.DiamondSquareGenerator(10, 0.5)
    generator = terrain.ImageGenerator('data/terrain_in.png', terrain.ImageGenerator.BITDEPTH_8)
    hydrerode = filters.HydraulicErosionFilter(100)
    thermal_erode = filters.ThermalErosionFilter(500)
    img_reader = reader.PILReader(reader.PILReader.BITDEPTH_8)

    terr = hydrerode(generator())
    img_reader(terr).save('terrain_out_hydrolic.png')
    terr = thermal_erode(terr)
    img_reader(terr).save('terrain_out.png')


if __name__ == '__main__':
    main()
