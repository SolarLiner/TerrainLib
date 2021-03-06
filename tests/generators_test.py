import random

import numpy

from terrainlib.generators.procedural import DiamondSquareGenerator, VoronoiGenerator
from terrainlib.terrain import Terrain


class TestDiamondSquareGenerator:
    def test_terrain_size(self):
        gen = DiamondSquareGenerator(5, 0.1)
        assert gen().size == 33

    @staticmethod
    def assert_terrains_equal(terr1: Terrain, terr2: Terrain):
        assert terr1 == terr2

    @staticmethod
    def assert_terrains_different(terr1: Terrain, terr2: Terrain):
        assert not terr1 == terr2

    def test_same_seed(self):
        for i in range(5):
            seed = random.random()
            gen1 = DiamondSquareGenerator(5, i/10, seed)
            gen2 = DiamondSquareGenerator(5, i/10, seed)

            yield self.assert_terrains_equal, gen1(), gen2()
    
    def test_diff_seeds(self):
        for i in range(5):
            seed1 = random.random()
            seed2 = random.randint(5, 1e80)
            
            gen1 = DiamondSquareGenerator(5, i/10, seed1)
            gen2 = DiamondSquareGenerator(5, i/10, seed2)

            yield self.assert_terrains_different, gen1(), gen2()

class TestVoronoiGenerator:
    def test_terrain_size(self):
        points = numpy.random.uniform(0, 1024, (50, 2))
        gen = VoronoiGenerator(1024)

        terr = gen(points.tolist())

        assert terr.size == 1024
