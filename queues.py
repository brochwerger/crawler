import queue

from abc import ABC, abstractmethod

class BasicQueue(ABC):

    def __init__(self):
        self.q = queue.Queue()

    def put(self, value):
        self.q.put(value)

    def get(self):
        return self.q.get()

