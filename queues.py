import queue

from abc import ABC, abstractmethod
from sys import maxsize

class BasicQueue(ABC):

    def __init__(self, maxsize=0):
        self.q = queue.Queue(maxisize=maxsize)

    def put(self, value):
        self.q.put(value)

    def get(self):
        return self.q.get()

