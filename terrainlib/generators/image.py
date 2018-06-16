"""Import existing terrain by importing their heights or otherwise definitive features of the terrain."""
# TerrainLib - A fast terrain generation library
# Copyright © 2018  Nathan "SolarLiner" Graule

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import numpy
from PIL import Image

from ..terrain import Terrain
from .base import TerrainGenerator


class PILInputGenerator(TerrainGenerator):
    """Generates terrain by copying greyscale data from an input image. This effectively imports the image as a Terrain
    object."""
    BITDEPTH_FLOAT = 1
    BITDEPTH_32 = 2**32-1
    BITDEPTH_16 = 2**16-1
    BITDEPTH_8 = 2**8-1

    def __init__(self, img, bitdepth):
        """Initialize the image reader.

        :param img: File path, or instance of ``PIL.Image`` containing the image to be used.
        :param bitdepth: One of ``PILInputGenerator.BITDEPTH_8, PILInputGenerator.BITDEPTH_16,
        PILInputGenerator.BITDEPTH_32, PILInputGenerator.BITDEPTH_FLOAT``. Used to scale the ``PIL.Image`` data by the
        correct amount to be used in the Terrain object.
        """
        if not bitdepth in [self.BITDEPTH_8, self.BITDEPTH_16, self.BITDEPTH_32, self.BITDEPTH_FLOAT]:
            raise TypeError('Bitdepth should be a valid number')
        self.bitdepth = bitdepth

        if isinstance(img, str):
            size = self._setup_image(Image.open(img), bitdepth)
        elif isinstance(img, Image.Image):
            size = self._setup_image(img, bitdepth)
        else:
            raise TypeError("Image can only be a string or a PIL.Image instance.")

    def __call__(self):
        """Generates the terrain from image data."""
        return Terrain(array=self.data)

    def _setup_image(self, image, bitdepth):
        """Crops the image to be a square. Should not be called directly."""
        if isinstance(image, Image.Image):
            width, height = image.size  # type: (int, int)
            short_side = min(width, height)   # type: int

            left = (width - short_side) / 2
            right = (width + short_side) / 2
            top = (height - short_side) / 2
            bottom = (height + short_side) / 2

            cropped_img = image.crop((left, top, right, bottom))
            self.data = numpy.divide(numpy.array(cropped_img, order='F'), bitdepth) # type: numpy.ndarray

            return short_side
