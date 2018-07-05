"""Custom lightweight task queue for threaded processing."""
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
import os
import queue
from threading import Thread


class BaseThreaded(queue.Queue, metaclass=abc.ABCMeta):
    """A task queue holds a list of tasks to be computed by a worker. Multiple workers can be made available,
    allowing tasks to be run in parallel. This is implemented as a base class"""
    num_workers: int

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.set_thread_count()

    def __call__(self, *args, **kwargs):
        self._start_workers()

    def set_thread_count(self, count=0):
        """Sets the number of threads, or get number from number of CPUs."""
        if count == 0:
            self.num_workers = os.cpu_count()
        else:
            self.num_workers = max(1, int(count))

    @abc.abstractmethod
    def task(self, *args, **kwargs):
        """Task that gets parallel processed."""

    def _start_workers(self):
        for _ in range(self.num_workers):
            t = Thread(target=self._worker)
            t.daemon = True
            t.start()

    def _worker(self):
        while True:
            item = self.get()
            if item is None:
                break
            self.task(*item)
            self.task_done()
