from terrainlib.generators.procedural import DiamondSquareGenerator
from terrainlib.filters.erosion import ThermalErosionFilter, StrataErosionFilter


class TestThermalErosion:
    def setup(self):
        gen = DiamondSquareGenerator(5, 0.1)
        eroder = ThermalErosionFilter(10)

        self.terr = gen()
        self.terr_eroded = eroder(self.terr)

    def test_same_terrain_size(self):
        assert self.terr.size == self.terr_eroded.size


class TestStrataErosion:
    def setup(self):
        gen = DiamondSquareGenerator(5, 0.1)
        eroder = StrataErosionFilter(8.5)

        self.terr = gen()
        self.terr_eroded = eroder(self.terr)

    def test_same_terrain_size(self):
        assert self.terr.size == self.terr_eroded.size