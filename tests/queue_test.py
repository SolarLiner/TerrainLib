from random import random
from time import sleep
from typing import Union

from terrainlib.queue import BaseThreaded


class BadSleepSort(BaseThreaded):
    def __call__(self, numbers: list):
        super().__call__()
        [self.put(x) for x in numbers]

    def task(self, number: Union[int, float]):
        sleep(number)
        print(number)


if __name__ == '__main__':
    sort = BadSleepSort()
    sort([random() * 3 for _ in range(20)])
    sort.join()
