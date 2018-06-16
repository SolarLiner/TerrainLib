import numpy
from nose.tools import raises

from terrainlib.terrain import Terrain


class TestTerrain:
    def test_accepts_size(self):
        terr = Terrain(256)

        assert terr.size == 256

    def test_accepts_array(self):
        terr = Terrain(numpy.random.uniform(size=(256,256)))

        assert terr.size == 256

    @raises(TypeError)
    def test_throws_on_nonsquare_array(self):
        terr = Terrain(array=numpy.random.uniform(size=(256,128)))

    @raises(TypeError)
    def test_throws_on_non_2d_array(self):
        terr = Terrain(array=numpy.random.uniform(size=128))

    def test_terrain_addition(self):
        arr1 = numpy.ones((128,128)) * 0.1
        arr2 = numpy.ones((128,128)) * 0.2
        res = numpy.ones((128,128)) * 0.3

        terr1 = Terrain(array=arr1)
        terr2 = Terrain(array=arr2)

        assert (terr1 + terr2)._heightmap == res

    def test_terrain_subtraction(self):
        arr1 = numpy.ones((128,128)) * 0.3
        arr2 = numpy.ones((128,128)) * 0.2
        res = numpy.ones((128,128)) * 0.1

        terr1 = Terrain(array=arr1)
        terr2 = Terrain(array=arr2)

        assert (terr1 - terr2)._heightmap == res

    def test_terrain_multiplication(self):
        arr1 = numpy.ones((128,128)) * 2.0
        arr2 = numpy.ones((128,128)) * .5
        res = numpy.ones((128,128))

        terr1 = Terrain(array=arr1)
        terr2 = Terrain(array=arr2)

        assert (terr1 * terr2)._heightmap == res

    def test_terrain_division(self):
        arr1 = numpy.ones((128,128)) * 2.0
        arr2 = numpy.ones((128,128)) * .5
        res = numpy.ones((128,128))

        terr1 = Terrain(array=arr1)
        terr2 = Terrain(array=arr2)

        assert (terr2 / terr1)._heightmap == res