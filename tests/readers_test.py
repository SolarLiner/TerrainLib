import math

from terrainlib.generators.procedural import DiamondSquareGenerator
from terrainlib.readers.image import PILImageReader


class TestImageExport:
    def setup(self):
        self.terrain = DiamondSquareGenerator(6, .1)()

    def test_save_image(self):
        for bitdepth in [PILImageReader.BITDEPTH_8, PILImageReader.BITDEPTH_16, PILImageReader.BITDEPTH_32, PILImageReader.BITDEPTH_FLOAT]:
            reader = PILImageReader(bitdepth)
            img = reader(self.terrain)
            img.save('terrain_test.tif')