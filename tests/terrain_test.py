import numpy
from nose.tools import raises

from terrainlib.terrain import Terrain


class TestTerrain:
    def test_accepts_size(self):
        terr = Terrain(size=256)

        assert terr.size == 256

    def test_accepts_array(self):
        array = numpy.random.uniform(size=(256, 256))
        terr = Terrain(array)

        assert terr.size == 256
        assert numpy.equal(terr._heightmap, array).all()

    @raises(TypeError)
    def test_throws_on_nonsquare_array(self):
        Terrain(array=numpy.random.uniform(size=(256, 128)))

    @raises(TypeError)
    def test_throws_on_non_2d_array(self):
        Terrain(array=numpy.random.uniform(size=128))

    def test_get_item_int(self):
        terr = Terrain(size=64)

        assert terr[0] == numpy.zeros(64)

    def test_get_item_float(self):
        arr = numpy.zeros((64, 64))
        arr[::2] = numpy.ones(64)

        terr = Terrain(array=arr)
        assert terr[0.5] == numpy.ones(64) * 0.5

    def test_get_item_tuple(self):
        terr = Terrain(array=numpy.ones((64, 64)))
        assert terr[0, 0] == 1

    def test_get_item_slice(self):
        arr = numpy.arange(0, 64).reshape((16, 16))
        terr = Terrain(array=arr)

        assert terr[::2] == arr[::2]
        assert terr[1:4, 1:4] == arr[1:4, 1:4]

    def test_terrain_addition(self):
        arr1 = numpy.ones((128, 128)) * 0.1
        arr2 = numpy.ones((128, 128)) * 0.2
        res = numpy.ones((128, 128)) * 0.3

        terr1 = Terrain(array=arr1)
        terr2 = Terrain(array=arr2)
        terr_res = terr1 + terr2

        assert terr_res == res

    def test_terrain_subtraction(self):
        arr1 = numpy.ones((128, 128)) * 0.3
        arr2 = numpy.ones((128, 128)) * 0.2
        res = numpy.ones((128, 128)) * 0.1

        terr1 = Terrain(array=arr1)
        terr2 = Terrain(array=arr2)
        terr_res = terr1 - terr2

        assert terr_res == res

    def test_terrain_multiplication(self):
        arr1 = numpy.ones((128, 128)) * 2.0
        arr2 = numpy.ones((128, 128)) * .5
        res = numpy.ones((128, 128))

        terr1 = Terrain(array=arr1)
        terr2 = Terrain(array=arr2)
        terr_res = (terr1 * terr2)

        assert terr_res == res

    def test_terrain_division(self):
        arr1 = numpy.ones((128, 128)) * 2.0
        arr2 = numpy.ones((128, 128)) * .5
        res = numpy.ones((128, 128))

        terr1 = Terrain(array=arr1)
        terr2 = Terrain(array=arr2)
        terr_res = terr2 / terr1

        assert terr_res == res

    def test_terrain_copy_array(self):
        arr = numpy.arange(0, 16 * 16).reshape((16, 16))
        terr = Terrain(array=arr)

        copy_arr = terr.to_array()  # type: numpy.ndarray
        assert numpy.equal(arr, copy_arr).all()

        copy_arr[::2] = 0
        assert not numpy.equal(arr, copy_arr).all()
