"""Abstract class definitions to setup the convention of Terrain Readers."""
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
import abc

from ..terrain import Terrain

class TerrainReader(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __call__(self, terrain: Terrain, *args, **kwargs):
        """Caller to process terrain data and output it into another format."""