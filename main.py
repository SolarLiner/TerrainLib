import logging
from itertools import product

import numpy
from PIL import Image

from terrainlib import reader, terrain

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)


def main():
    terr = terrain.ImageGenerator('data/terrain_input.png', terrain.ImageGenerator.BITDEPTH_16)
    img_reader = reader.PILReader(reader.PILReader.BITDEPTH_8)
    img = img_reader(terr)
    img.save('terrain_out.png')
    

if __name__ == '__main__':
    main()
