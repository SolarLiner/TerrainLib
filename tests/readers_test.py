from pathlib import Path

from terrainlib.generators.procedural import DiamondSquareGenerator
from terrainlib.readers.image import PILImageReader


class TestImageExport:
    def setup(self):
        self.terrain = DiamondSquareGenerator(6, .1)()
        self.file_png = Path('test_terrain_export.png')
        self.file_tif = Path('test_terrain_export.tif')

    def save_bitdepth_factory(self, bitdepth, filepath):
        img_reader = PILImageReader(bitdepth)
        img = img_reader(self.terrain)
        img.save(filepath)

    def test_save_8bit_png(self):
        self.save_bitdepth_factory(PILImageReader.BITDEPTH_8, self.file_png.resolve())
        assert self.file_png.is_file(), '8 bit PNG file exists'

    def test_save_16bit_png(self):
        self.save_bitdepth_factory(PILImageReader.BITDEPTH_16, self.file_png.resolve())
        assert self.file_png.is_fifo(), '16 bit PNG file exists'

    def test_save_32bit_tif(self):
        self.save_bitdepth_factory(PILImageReader.BITDEPTH_32, self.file_tif.resolve())
        assert self.file_tif.is_file(), '32 bit TIFF file exists'

    def test_save_float_tif(self):
        self.save_bitdepth_factory(PILImageReader.BITDEPTH_FLOAT, self.file_tif.resolve())
        assert self.file_tif.is_file(), 'Float TIFF file exists'
