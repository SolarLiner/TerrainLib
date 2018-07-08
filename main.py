import logging
import time
from datetime import timedelta

from terrainlib.filters.erosion import StrataFilter, ThermalErosionFilter
from terrainlib.generators.procedural import DiamondSquareGenerator
from terrainlib.readers.image import PILImageReader


class ElapsedFormatter(logging.Formatter):
    def __init__(self, fmt=None):
        super().__init__(fmt)
        self.start = time.time()

    def format(self, record):
        message = super(__class__, self).format(record)
        elapsed_time = timedelta(seconds=record.created - self.start)
        return '[{} s] {}'.format(elapsed_time, message)


logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

sh = logging.FileHandler('debug.log', 'w')
sh.setFormatter(ElapsedFormatter('%(levelname)s @ %(module)s: %(message)s'))


def main():
    # generator = PILInputGenerator('data/terrain_in.png', PILInputGenerator.BITDEPTH_8)
    generator = DiamondSquareGenerator(10, 0.2)
    # hydrerode = HydraulicErosionFilter(100)
    strata = StrataFilter(22.8)
    thermal_erode = ThermalErosionFilter(20)
    img_reader = PILImageReader(PILImageReader.BITDEPTH_8)

    terr = strata(generator())
    img_reader(terr).save('terrain_strata.png')
    terr = thermal_erode(terr)
    img_reader(terr).save('terrain_out.png')
    # voronoi = VoronoiGenerator(1024)
    # erosion = ThermalErosionFilter(150)
    # reader = PILImageReader(PILImageReader.BITDEPTH_8)

    # points = numpy.random.uniform(high=1024, size=(50,2))
    # terr = erosion(voronoi(points.tolist()))
    # img = reader(terr)
    # img.save('terrain_out.png')


if __name__ == '__main__':
    main()
