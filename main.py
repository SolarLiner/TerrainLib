import logging
from itertools import product

import numpy
from PIL import Image

from terrainlib import reader, terrain

logging.basicConfig(filename='debug.log',format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)


def main():
    terrain_gen = terrain.DiamondSquareGenerator(8, 0.1)
    terr = terrain_gen()
    img_reader = reader.PILReader()
    img = img_reader(terr)
    with open('terrain_final.txt', mode='w') as f:
        f.write(repr(terr))
    img.convert('RGB').save('terrain_final.png')

if __name__ == '__main__':
    main()
