import sys
import queue
import pika
import pickle

from abc import ABC, abstractmethod
from sys import maxsize

class BasicQueue(ABC):

    def __init__(self, maxsize=0):
        self.q = queue.Queue(maxisize=maxsize)

    def put(self, value):
        self.q.put(value)

    def get(self):
        return self.q.get()

class RabbitMQueue(BasicQueue):

    def __init__(self, server, queue):
        self.server = server
        self.queue = queue
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.server))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue)

    def put(self, value):
        self.channel.basic_publish(exchange='', routing_key=self.queue, body=pickle.dumps(value))

    def get(self):
        data = None
        for method_frame, properties, body in self.channel.consume(self.queue):
            data = pickle.loads(body)
            self.channel.basic_ack(method_frame.delivery_tag)
            break
        return data

if __name__ == "__main__":

    rmq = RabbitMQueue(server='localhost',queue='hello')

    if len(sys.argv) >= 2 and sys.argv[1] == 'send':
        print(" [x] Sent 'Hello World!'")
        rmq.put(sys.argv[1:])
    else:
        message = rmq.get()
        print(message)

    print("Good bye")